"""
MT5 Grid Trading Bot com Martingale
Abre posicoes em grade, dobra lote a cada nivel
Fecha TODAS quando atingir meta de lucro
"""

import MetaTrader5 as mt5
import time
import random
import logging
from datetime import datetime, timedelta

# Suporte a cores no terminal (colorama). Se nao estiver instalado, usamos fallback sem cor.
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except Exception:
    class _NoColor:
        RESET_ALL = ''
        RED = ''
        GREEN = ''
        YELLOW = ''
        CYAN = ''
    Fore = _NoColor()
    Style = _NoColor()

# Funcoes utilitarias de log colorido
def _cinfo(msg: str):
    # Mensagens informativas coloridas com timestamp
    try:
        now = datetime.now()
        ts = f"{now:%Y-%m-%d %H:%M:%S},{int(now.microsecond/1000):03d}"
        # timestamp in default color, message in cyan
        print(f"{ts} ", end='')
        print(Fore.CYAN + f"- INFO - {msg}" + Style.RESET_ALL)
    except Exception:
        try:
            print(msg)
        except Exception:
            pass

def _cwarn(msg: str):
    # Avisos criticos: imprime em vermelho e manda para logging.warning
    try:
        now = datetime.now()
        ts = f"{now:%Y-%m-%d %H:%M:%S},{int(now.microsecond/1000):03d}"
        # timestamp in default color, warning in red
        print(f"{ts} ", end='')
        print(Fore.RED + f"- WARNING - {msg}" + Style.RESET_ALL)
    except Exception:
        try:
            print(msg)
        except Exception:
            pass
    # não chamar logging.warning aqui para evitar duplicação (a linha já é impressa colorida acima)

def _csuccess(msg: str):
    # Mensagens de sucesso/close: imprime em verde com timestamp
    try:
        now = datetime.now()
        ts = f"{now:%Y-%m-%d %H:%M:%S},{int(now.microsecond/1000):03d}"
        # timestamp in default color, success message in green
        print(f"{ts} ", end='')
        print(Fore.GREEN + f"- INFO - {msg}" + Style.RESET_ALL)
    except Exception:
        try:
            print(msg)
        except Exception:
            pass

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MT5GridBot:
    def __init__(self, symbol='XAUUSDm', grid_distance=500, initial_lot=0.01,
                 daily_profit_target=100.0, max_levels=10,
                 take_profit_points=None, reset_hour=0, reset_minute=0,
                 min_floating_profit=10.0, min_level_for_floating=4,
                 min_grid_distance_points=1200, min_take_profit_points=1800,
                 lot_schedule=None, enable_hedge_with_schedule=False):
        """
        Grid Trading Bot com controle de lucro DIARIO
        
        Args:
            symbol: Simbolo para operar
            grid_distance: Distancia entre niveis (em pontos)
            initial_lot: Lote inicial
            daily_profit_target: Meta de lucro DIARIO ($) - para quando atingir
            max_levels: Maximo de niveis de grid
        """
        self.symbol = symbol
        self.grid_distance = grid_distance
        self.initial_lot = initial_lot
        self.daily_profit_target = daily_profit_target
        self.max_levels = max_levels
        self.martingale_multiplier = 2.0  # Dobra o lote
        # Take profit em pontos (padrão: mesma distancia do grid)
        self.take_profit_points = take_profit_points if take_profit_points is not None else grid_distance
        # Horario do reset diario (hora, minuto) — padrão meia-noite
        self.reset_hour = reset_hour
        self.reset_minute = reset_minute
        # Sequencia de lotes opcional (lista). Se fornecida, usa esses lotes por nivel.
        # Ex: [0.01, 0.03, 0.06, 0.12]
        # Se None, usamos uma sequencia padrao segura (evita default mutavel)
        if lot_schedule is None:
            lot_schedule = [0.01, 0.03, 0.06, 0.12, 0.24, 0.48, 0.96, 1.92, 3.84, 7.68]
        self.lot_schedule = lot_schedule
        # Quando True, permite aplicar hedge mesmo se lot_schedule estiver presente.
        # Quando False (padrão), o bot abrirá estritamente com os valores de lot_schedule sem somar hedge.
        self.enable_hedge_with_schedule = bool(enable_hedge_with_schedule)
        # Valor minimo de lucro flutuante para considerar fechamento por floating positivo
        self.min_floating_profit = min_floating_profit
        # Nivel minimo do grid (numero de passos) a partir do qual o floating entra em vigor
        self.min_level_for_floating = min_level_for_floating
        # Distancia minima do grid (em pontos) para abrir niveis
        self.min_grid_distance_points = min_grid_distance_points
        # Take profit minimo (em pontos) usado ao abrir posicoes
        self.min_take_profit_points = min_take_profit_points
        
        # Gera magic_number unico por instancia para evitar conflitos com outros EAs
        try:
            seed = int(time.time() * 1000) ^ id(self)
            random.seed(seed)
            self.magic_number = random.randint(100000, 99999999)
        except Exception:
            self.magic_number = 789456123
        self.running = False
        
        # Grid state
        self.grid_levels = []  # Lista de niveis de preco
        self.last_buy_level = None
        self.last_sell_level = None
        
        # Daily tracking
        self.daily_profit = 0.0
        self.daily_profit_baseline = 0.0  # Lucro no momento do reset
        self.last_reset_date = None
        self.max_drawdown = 0.0  # Maior prejuízo flutuante
        self.peak_equity = 0.0  # Maior equity atingido
        self.target_reached_today = False  # Flag para saber se ja fechou hoje
        # Maior lucro flutuante atingido desde o ultimo ciclo/reset (para trailing)
        self.max_open_profit = 0.0

        # Reopen-on-return (quando o preco retorna ao preco de entrada do grid)
        # Habilita reabertura automática de niveis retornando ao preco de entrada
        # Apenas para niveis iniciais (ate self.reopen_max_level)
        self.reopen_on_return = True
        self.reopen_max_level = 3
        # Tolerancia em pontos para considerar "volta ao preco" (pontos do simbolo)
        self.reopen_tolerance_points = 5
        # Cooldown em segundos para evitar reabrir repetidamente o mesmo nivel
        self.reopen_cooldown = 60
        # Historico de reabrir: chaves ('buy'|'sell', level) -> timestamp
        self._reopen_history = {}
        
    def initialize(self, login=None, password=None, server=None):
        """Inicializa conexao com MT5"""
        if not mt5.initialize():
            logging.error(f"MT5 initialize falhou: {mt5.last_error()}")
            return False
        
        # Login se fornecido
        if login and password and server:
            if not mt5.login(login, password, server):
                logging.error(f"Login falhou: {mt5.last_error()}")
                return False
            _cinfo(f"[OK] Login realizado: {login}")
        
        # Verifica simbolo
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logging.error(f"Simbolo {self.symbol} nao encontrado")
            return False
        
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                logging.error(f"Falha ao selecionar {self.symbol}")
                return False
        
        _cinfo(f"[OK] Bot Grid inicializado para {self.symbol}")
        return True
    
    def shutdown(self):
        """Desconecta MT5"""
        mt5.shutdown()
        _cinfo("[OK] MT5 desconectado")
    
    def get_account_info(self):
        """Obtem informacoes da conta"""
        account_info = mt5.account_info()
        if account_info is None:
            return None
        
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'profit': account_info.profit,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free
        }
    
    def get_current_price(self):
        """Obtem preco atual"""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None, None
        return tick.bid, tick.ask
    
    def get_open_positions(self):
        """Obtem posicoes abertas do bot"""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return []
        
        # Filtra por magic number
        return [p for p in positions if p.magic == self.magic_number]
    
    def get_total_profit(self):
        """Calcula lucro total de todas posicoes"""
        positions = self.get_open_positions()
        return sum(p.profit for p in positions)
    
    def get_daily_profit(self):
        """Calcula lucro DIARIO = Trades fechados + Lucro flutuante das posições abertas"""
        # Novo método: calcula lucro desde o baseline usando equity
        # A conta MT5: equity = balance + open_profit
        # Se armazenarmos baseline_balance no reset, então lucro total desde reset = equity - baseline_balance
        account_info = mt5.account_info()
        if account_info is None:
            return 0.0

        current_equity = account_info.equity
        profit_since_reset = current_equity - self.daily_profit_baseline
        return profit_since_reset
    
    def close_all_positions(self):
        """Fecha todas as posicoes abertas"""
        positions = self.get_open_positions()
        
        if not positions:
            return True
        
        _cinfo(f"[FECHANDO] {len(positions)} posicoes...")
        
        for pos in positions:
            # Define tipo de ordem oposta
            if pos.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            
            base_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "magic": self.magic_number,
                "comment": "Grid Close All",
                "type_time": mt5.ORDER_TIME_GTC,
            }

            # Tenta modos de filling num ordem de compatibilidade: RETURN -> IOC -> FOK
            fillings = [mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK]
            closed = False
            for f in fillings:
                # captura balance antes do fechamento para calcular lucro realizado
                try:
                    acc_before = mt5.account_info()
                    balance_before = acc_before.balance if acc_before is not None else None
                except Exception:
                    balance_before = None

                req = base_request.copy()
                req["type_filling"] = f
                result = mt5.order_send(req)
                if result is None:
                    logging.error(f"Erro ao enviar ordem de fechamento #{pos.ticket}: resultado None")
                    continue
                _cinfo(f"Fechar #{pos.ticket} tentativa filling={f} -> retcode={getattr(result, 'retcode', 'NA')} comment={getattr(result, 'comment', '')}")
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    _cinfo(f"[OK] Posicao #{pos.ticket} fechada (filling={f})")
                    closed = True
                    # Calcula lucro realizado usando balance antes/depois quando possivel
                    realized = None
                    try:
                        acc_after = mt5.account_info()
                        balance_after = acc_after.balance if acc_after is not None else None
                        if balance_before is not None and balance_after is not None:
                            realized = balance_after - balance_before
                    except Exception:
                        realized = None

                    # Imprime resumo da posicao fechada com lucro realizado (timestamp em branco + cores)
                    try:
                        now = datetime.now()
                        ts = f"{now:%Y-%m-%d %H:%M:%S},{int(now.microsecond/1000):03d}"
                        # separador superior
                        print(f"{ts} ", end='')
                        print(Fore.CYAN + "------------------------------------------------------------" + Style.RESET_ALL)
                        # linha de close em verde
                        if realized is not None:
                            print(f"{ts} ", end='')
                            print(Fore.GREEN + f"CLOSE POSITION #{pos.ticket} | LUCRO_DA_POSICAO: ${realized:.2f}" + Style.RESET_ALL)
                        else:
                            print(f"{ts} ", end='')
                            print(Fore.GREEN + f"CLOSE POSITION #{pos.ticket} | LUCRO_DA_POSICAO: ${pos.profit:.2f}" + Style.RESET_ALL)
                        # separador inferior
                        print(f"{ts} ", end='')
                        print(Fore.CYAN + "------------------------------------------------------------" + Style.RESET_ALL)
                    except Exception:
                        pass
                    break
            if not closed:
                logging.error(f"Falha ao fechar posicao #{pos.ticket}: nenhum modo de filling aceito")
        
        return True
    
    def get_next_lot_size(self, current_level):
        """Calcula tamanho do lote com martingale + hedge para suprir perdas"""
        # Base do lote: pode vir de lot_schedule ou do martingale
        if self.lot_schedule and isinstance(self.lot_schedule, (list, tuple)) and len(self.lot_schedule) > 0:
            if current_level < len(self.lot_schedule):
                base_lot = float(self.lot_schedule[current_level])
            else:
                base_lot = float(self.lot_schedule[-1])
        else:
            # Martingale base: dobra a cada nivel
            base_lot = self.initial_lot * (self.martingale_multiplier ** current_level)
        
        # Calcula hedge para compensar prejuízo das posições abertas
        # Hedge = valor que precisa ganhar para cobrir todas as perdas abertas
        # Se o usuário forneceu `lot_schedule`, NÃO somamos hedge: abrimos estritamente os lotes da lista.
        open_profit = self.get_total_profit()  # negativo = prejuízo
        hedge_lot = 0.0

        use_schedule = bool(self.lot_schedule and isinstance(self.lot_schedule, (list, tuple)) and len(self.lot_schedule) > 0)
        if use_schedule:
            # Quando usamos schedule, não aplicamos hedge automaticamente — mantemos os valores da lista.
            if open_profit < 0:
                _cinfo(f"lot_schedule ativo -> Hedge desabilitado (abrindo apenas base da lista) | OpenProfit={open_profit:.2f}")
        else:
            if open_profit < 0:  # Se tem prejuízo aberto
                symbol_info = mt5.symbol_info(self.symbol)
                if symbol_info:
                    # Tenta calcular hedge em lotes usando o valor do tick/lot quando disponivel
                    loss_absolute = abs(open_profit)
                    hedge_lot = 0.0
                    tick_value = getattr(symbol_info, 'trade_tick_value', None)
                    # trade_tick_value representa quanto vale um tick por 1 lote em conta
                    if tick_value and tick_value > 0:
                        # loss / (tick_value * grid_distance) -> lot necessária
                        hedge_lot = loss_absolute / (tick_value * self.grid_distance)
                    else:
                        # Fallback (menos preciso): usa point como proxy, mas com limitador
                        point = symbol_info.point
                        if point and self.grid_distance * point > 0:
                            hedge_lot = loss_absolute / (self.grid_distance * point)
                        else:
                            hedge_lot = 0.0
                    hedge_lot = max(hedge_lot, 0)
                    # Limita hedge para não gerar lotes astronomicos: max 5x do lote base neste nivel
                    # NÃO sobrescreve `base_lot` — usa o base_lot já determinado (pode vir de lot_schedule)
                    max_hedge = base_lot * 5
                    if hedge_lot > max_hedge:
                        _cinfo(f"Hedge calculado {hedge_lot:.2f} excede max {max_hedge:.2f}, limitando")
                        hedge_lot = max_hedge
        hedge_lot = 0.0
        
        if open_profit < 0:  # Se tem prejuízo aberto
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info:
                # Tenta calcular hedge em lotes usando o valor do tick/lot quando disponivel
                loss_absolute = abs(open_profit)
                hedge_lot = 0.0
                tick_value = getattr(symbol_info, 'trade_tick_value', None)
                # trade_tick_value representa quanto vale um tick por 1 lote em conta
                if tick_value and tick_value > 0:
                    # loss / (tick_value * grid_distance) -> lot necessária
                    hedge_lot = loss_absolute / (tick_value * self.grid_distance)
                else:
                    # Fallback (menos preciso): usa point como proxy, mas com limitador
                    point = symbol_info.point
                    if point and self.grid_distance * point > 0:
                        hedge_lot = loss_absolute / (self.grid_distance * point)
                    else:
                        hedge_lot = 0.0
                hedge_lot = max(hedge_lot, 0)
                # Limita hedge para não gerar lotes astronomicos: max 5x do lote base neste nivel
                base_lot = self.initial_lot * (self.martingale_multiplier ** current_level)
                max_hedge = base_lot * 5
                if hedge_lot > max_hedge:
                    _cinfo(f"Hedge calculado {hedge_lot:.2f} excede max {max_hedge:.2f}, limitando")
                    hedge_lot = max_hedge
        
        # Total = base + hedge
        lot = base_lot + hedge_lot
        
        # Limita ao maximo permitido
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info:
            lot = min(lot, symbol_info.volume_max)
            lot = max(lot, symbol_info.volume_min)

            # Arredonda para step
            lot_step = symbol_info.volume_step
            lot = round(lot / lot_step) * lot_step

            # Log detalhado
            if hedge_lot > 0:
                _cinfo(f"Lot Nivel {current_level}: Base={base_lot:.4f} + Hedge={hedge_lot:.4f} = Total={lot:.4f}")
        
        return lot
    
    def open_grid_position(self, order_type, price, level):
        """Abre posicao no nivel do grid"""
        lot_size = self.get_next_lot_size(level)
        # TP: usa take_profit_points (configuravel) aplicando o minimo configurado
        tp_points = max(self.take_profit_points, self.min_take_profit_points)

        # Informacoes do simbolo para validar stops e lotes
        symbol_info = mt5.symbol_info(self.symbol)
        point = symbol_info.point if symbol_info else mt5.symbol_info(self.symbol).point

        # Garante que a distancia do TP respeite o minimo do broker (trade_stops_level)
        min_stop_points = getattr(symbol_info, 'trade_stops_level', 0) if symbol_info else 0
        required_points = max(tp_points, min_stop_points)

        # Calcula preco de TP ajustado conforme minimo
        if order_type == mt5.ORDER_TYPE_BUY:
            tp_price = price + (required_points * point)
        else:
            tp_price = price - (required_points * point)
        
        # Normaliza precos
        digits = symbol_info.digits if symbol_info else mt5.symbol_info(self.symbol).digits
        price = round(price, digits)
        tp_price = round(tp_price, digits)

        # Log se tivemos que ajustar o TP devido a requisitos do broker
        if required_points != tp_points:
            _cinfo(f"Ajustado TP para respeitar trade_stops_level: required_points={required_points} (original={tp_points})")
        
        base_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "tp": tp_price,
            "magic": self.magic_number,
            "comment": f"Grid L{level}",
            "type_time": mt5.ORDER_TIME_GTC,
        }
        # Log dos limites de lote para diagnostico
        if symbol_info:
            _cinfo(f"Symbol volumes: min={symbol_info.volume_min} max={symbol_info.volume_max} step={symbol_info.volume_step} | Pedido lote={lot_size}")

        # Tenta modos de filling em ordem preferencial (IOC/FOK/RETURN)
        fillings = [mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]
        result = None
        for f in fillings:
            req = base_request.copy()
            req["type_filling"] = f
            result = mt5.order_send(req)
            if result is None:
                logging.error(f"Envio falhou (None) filling={f})")
                continue
            _cinfo(f"Abrir Grid tentativa filling={f} -> retcode={getattr(result, 'retcode', 'NA')} comment={getattr(result, 'comment', '')}")
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                order_name = "BUY" if order_type == mt5.ORDER_TYPE_BUY else "SELL"
                _cinfo(f"[GRID {order_name}] Nivel {level} | Lote: {lot_size:.2f} | Preco: {price} (filling={f})")
                return True

        # Se chegou aqui, todas as tentativas falharam; tenta reduzir lote para volume_min uma vez
        if result is not None:
            logging.error(f"Erro ao abrir grid: {getattr(result, 'comment', '')} (retcode: {getattr(result, 'retcode', 'NA')})")
            if symbol_info and lot_size != symbol_info.volume_min:
                fallback_lot = symbol_info.volume_min
                _cinfo(f"Tentando fallback com lote minimo: {fallback_lot}")
                base_request["volume"] = fallback_lot
                for f in fillings:
                    req = base_request.copy()
                    req["type_filling"] = f
                    result2 = mt5.order_send(req)
                    if result2 is None:
                        logging.error(f"Fallback envio falhou (None) filling={f})")
                        continue
                    _cinfo(f"Fallback tentativa filling={f} -> retcode={getattr(result2, 'retcode', 'NA')} comment={getattr(result2, 'comment', '')}")
                    if result2.retcode == mt5.TRADE_RETCODE_DONE:
                        order_name = "BUY" if order_type == mt5.ORDER_TYPE_BUY else "SELL"
                        _cinfo(f"[GRID {order_name}] Nivel {level} | Lote: {fallback_lot:.2f} | Preco: {price} (filling={f})")
                        return True
                logging.error("Fallback com lote minimo falhou")
        else:
            logging.error("Erro ao abrir grid: resultado de order_send foi None em todas as tentativas")

        return False
    
    def reset_daily_counters(self):
        """Reseta contadores diarios no horario configurado (self.reset_hour:self.reset_minute)"""
        now = datetime.now()
        reset_dt_today = datetime(now.year, now.month, now.day, self.reset_hour, self.reset_minute)

        # Inicializa last_reset_date de forma consistente
        if self.last_reset_date is None:
            if now < reset_dt_today:
                self.last_reset_date = (now.date() - timedelta(days=1))
            else:
                self.last_reset_date = now.date()

        # Se passou do horario de reset e ainda nao resetamos hoje, faz o reset
        if now >= reset_dt_today and self.last_reset_date < now.date():
            today = now.date()
            _cinfo(f"[RESET DIARIO] Novo ciclo: {today} {self.reset_hour:02d}:{self.reset_minute:02d}")
            self.daily_profit = 0.0
            self.daily_profit_baseline = 0.0  # Zera baseline no novo ciclo
            self.max_drawdown = 0.0  # Zera drawdown
            self.peak_equity = 0.0  # Zera peak equity
            self.max_open_profit = 0.0
            self.target_reached_today = False  # Reseta flag
            self.last_buy_level = None
            self.last_sell_level = None
            self.last_reset_date = today
    
    def reset_now(self):
        """RESETA TUDO IMEDIATAMENTE - Recomeça do zero"""
        from datetime import datetime
        _cinfo("=" * 60)
        _cinfo("[RESET MANUAL] Zerando todos os contadores...")
        #_cinfo("=" * 60)
        # Fecha posicoes abertas para realmente reiniciar do ZERO
        try:
            self.close_all_positions()
            # Aguarda alguns instantes até que as posicoes sumam (timeout curto)
            wait_total = 0.0
            while wait_total < 5.0:
                open_pos = self.get_open_positions()
                if not open_pos:
                    break
                time.sleep(0.5)
                wait_total += 0.5
            else:
                logging.error("Algumas posicoes ainda abertas apos timeout de fechamento")
        except Exception:
            logging.error("Falha ao fechar posicoes durante reset; prosseguindo mesmo assim")

        # Salva a equity atual como baseline (inclui lucro flutuante) para que
        # o lucro desde o reset comece em zero mesmo que existissem posicoes.
        account_info = mt5.account_info()
        baseline_equity = self.daily_profit_baseline = self.peak_equity = account_info.equity if account_info else 0.0
        self.daily_profit_baseline = self.peak_equity = baseline_equity
        _cinfo(f"[BASELINE] Equity no reset: ${baseline_equity:.2f}")
        #logging.warning(f"[BASELINE] Lucros futuros (fechados + flutuantes) serao contados a partir desse baseline")
        
       
        # Atualiza data de reset
        self.last_reset_date = datetime.now().date()
        # Reseta pico de lucro flutuante
        self.max_open_profit = 0.0
        
        #logging.warning("[OK] Contadores zerados! Bot recomeça do ZERO")
        #logging.warning(f"[OK] Lucro diario resetado para: $0.00")
        #_cinfo(f"[OK] Niveis de grid resetados")
        _cinfo("=" * 60)

    def reset_cycle(self):
        """Reseta apenas o ciclo de niveis/lotes sem alterar o lucro diario/baseline.

        Fecha posicoes abertas e recomeça os niveis (last_buy_level/last_sell_level)
        sem tocar em `daily_profit_baseline`, `daily_profit` ou `last_reset_date`.
        """
        _cinfo("[RESET CICLO] Reiniciando ciclo de lotes (sem zerar lucro diario)")
        try:
            self.close_all_positions()
            # Aguarda breve até que as posicoes sumam
            wait_total = 0.0
            while wait_total < 5.0:
                open_pos = self.get_open_positions()
                if not open_pos:
                    break
                time.sleep(0.5)
                wait_total += 0.5
            else:
                logging.error("Algumas posicoes ainda abertas apos timeout de fechamento (reset_cycle)")
        except Exception:
            logging.error("Falha ao fechar posicoes durante reset_cycle; prosseguindo mesmo assim")

        # Para evitar que o bot abra imediatamente BUY e SELL ao reiniciar o ciclo,
        # defini os "last levels" para o preco atual. Assim o grid somente
        # abrirá novos niveis quando o preco se mover o suficiente.
        bid, ask = self.get_current_price()
        if bid is not None and ask is not None:
            current_price = (bid + ask) / 2
            self.last_buy_level = current_price
            self.last_sell_level = current_price
        else:
            # Se nao conseguimos o preco, mantemos como None (comportamento antigo)
            self.last_buy_level = None
            self.last_sell_level = None

        # Reseta pico de lucro flutuante ao reiniciar ciclo de lotes
        self.max_open_profit = 0.0

        _cinfo("[OK] Ciclo de lotes reiniciado; lucro diario preservado")
    
    def check_and_open_grid_levels(self):
        """Verifica e abre novos niveis de grid"""
        # Verifica se ja atingiu meta diaria
        if self.daily_profit >= self.daily_profit_target:
            return  # NAO abre novas posicoes
        
        bid, ask = self.get_current_price()
        if bid is None:
            return
        
        current_price = (bid + ask) / 2
        positions = self.get_open_positions()
        
        # Conta niveis de compra e venda
        buy_positions = [p for p in positions if p.type == mt5.POSITION_TYPE_BUY]
        sell_positions = [p for p in positions if p.type == mt5.POSITION_TYPE_SELL]
        
        buy_level = len(buy_positions)
        sell_level = len(sell_positions)
        
        point = mt5.symbol_info(self.symbol).point
        # Aplica distancia minima configurada (em pontos)
        effective_grid_distance = max(self.grid_distance, self.min_grid_distance_points)
        grid_distance_price = effective_grid_distance * point
        
        opened_this_cycle = False

        # === GRID DE COMPRA (abaixo do preco) ===
        if buy_level < self.max_levels:
            # Calcula onde deveria estar o proximo nivel de compra
            if self.last_buy_level is None:
                # Primeiro nivel: um pouco abaixo do preco atual
                next_buy_price = current_price - grid_distance_price
            else:
                # Proximo nivel: distancia do ultimo
                next_buy_price = self.last_buy_level - grid_distance_price
            
            # Abre se preco caiu ate o nivel
            if current_price <= next_buy_price or self.last_buy_level is None:
                # Marca que estamos tentando abrir nesta iteracao para evitar abrir o outro lado
                opened_this_cycle = True
                if self.open_grid_position(mt5.ORDER_TYPE_BUY, ask, buy_level):
                    self.last_buy_level = ask
        
        # === GRID DE VENDA (acima do preco) ===
        if sell_level < self.max_levels:
            # Calcula onde deveria estar o proximo nivel de venda
            if self.last_sell_level is None:
                # Primeiro nivel: um pouco acima do preco atual
                next_sell_price = current_price + grid_distance_price
            else:
                # Proximo nivel: distancia do ultimo
                next_sell_price = self.last_sell_level + grid_distance_price
            
            # Abre se preco subiu ate o nivel
            # Evita abrir SELL na mesma iteracao se ja tentamos abrir BUY agora
            if (current_price >= next_sell_price or self.last_sell_level is None) and not opened_this_cycle:
                # Marca tentativa e tenta abrir
                opened_this_cycle = True
                if self.open_grid_position(mt5.ORDER_TYPE_SELL, bid, sell_level):
                    self.last_sell_level = bid
        # === Reopen on return: tenta reabrir niveis quando o preco retorna ao preco de entrada ===
        # Aplica somente se a opcao estiver habilitada e nao abrimos nada nesta iteracao
        try:
            if self.reopen_on_return and not opened_this_cycle:
                tolerance_price = self.reopen_tolerance_points * point
                now_ts = time.time()

                # BUY: reabre se o preco voltou ao ultimo nivel de compra e ainda estamos abaixo do limite
                if buy_level < self.reopen_max_level and self.last_buy_level is not None:
                    if abs(current_price - self.last_buy_level) <= tolerance_price:
                        key = ('buy', buy_level)
                        last = self._reopen_history.get(key, 0)
                        if now_ts - last >= self.reopen_cooldown:
                            _cinfo(f"[REOPEN BUY] Preco retornou ao nivel de entrada {self.last_buy_level} (nivel alvo {buy_level}) -> tentando reabrir")
                            if self.open_grid_position(mt5.ORDER_TYPE_BUY, ask, buy_level):
                                self.last_buy_level = ask
                                self._reopen_history[key] = now_ts
                                opened_this_cycle = True

                # SELL: reabre se o preco voltou ao ultimo nivel de venda e ainda estamos abaixo do limite
                if not opened_this_cycle and sell_level < self.reopen_max_level and self.last_sell_level is not None:
                    if abs(current_price - self.last_sell_level) <= tolerance_price:
                        key = ('sell', sell_level)
                        last = self._reopen_history.get(key, 0)
                        if now_ts - last >= self.reopen_cooldown:
                            _cinfo(f"[REOPEN SELL] Preco retornou ao nivel de entrada {self.last_sell_level} (nivel alvo {sell_level}) -> tentando reabrir")
                            if self.open_grid_position(mt5.ORDER_TYPE_SELL, bid, sell_level):
                                self.last_sell_level = bid
                                self._reopen_history[key] = now_ts
                                opened_this_cycle = True
        except Exception:
            logging.error("Erro ao processar reopen_on_return")
    
    def run(self):
        """Loop principal do bot"""
        self.running = True
        _cinfo("[INICIO] Bot Grid rodando...")
        _cinfo(f"Distancia Grid: {self.grid_distance} pontos")
        _cinfo(f"Lote Inicial: {self.initial_lot}")
        _cinfo(f"Meta de Lucro DIARIO: ${self.daily_profit_target:.2f}")
        _cinfo(f"Max Niveis: {self.max_levels}")
        _cinfo(f"Min Floating para fechar ciclo: ${self.min_floating_profit:.2f} (aplica a partir do nivel {self.min_level_for_floating})")
        _cinfo(f"Min Grid Distance (pontos): {self.min_grid_distance_points} | Min TP (pontos): {self.min_take_profit_points}")
        print()
        
        while self.running:
            try:
                # Reseta contadores a meia-noite
                self.reset_daily_counters()
                
                # Atualiza lucro diario
                self.daily_profit = self.get_daily_profit()
                
                # Calcula drawdown (lucro flutuante de posições abertas)
                open_profit = self.get_total_profit()
                account = self.get_account_info()

                # Atualiza pico de lucro flutuante (para comportamento trailing)
                try:
                    self.max_open_profit = max(self.max_open_profit, open_profit)
                except Exception:
                    self.max_open_profit = open_profit if open_profit is not None else self.max_open_profit

                # Se o floating estiver positivo, fecha tudo e recomeça do nivel 0
                try:
                    positions_now = self.get_open_positions()
                    if positions_now:
                        buy_positions = [p for p in positions_now if p.type == mt5.POSITION_TYPE_BUY]
                        sell_positions = [p for p in positions_now if p.type == mt5.POSITION_TYPE_SELL]
                        highest_level = max(len(buy_positions), len(sell_positions))
                        # Aplica regra: só fecha por floating se estiver exatamente no nivel configurado
                        # Ex.: se min_level_for_floating == 4, fecha apenas quando highest_level == 4.
                        # Mantemos o comportamento de trailing (pico de floating) dentro desse mesmo nivel.
                        if highest_level == self.min_level_for_floating:
                            if open_profit >= self.min_floating_profit:
                                _cwarn(f"[FLOATING POSITIVO] Open profit={open_profit:.2f} >= min_floating={self.min_floating_profit:.2f} e nivel={highest_level} == min_level={self.min_level_for_floating} -> Fechando e recomeçando ciclo (preservando lucro diario)")
                                self.reset_cycle()
                                time.sleep(1)
                                continue
                            if self.max_open_profit >= self.min_floating_profit and open_profit > 0:
                                _cwarn(f"[TRAILING] Pico de floating {self.max_open_profit:.2f} >= min_floating={self.min_floating_profit:.2f} e open_profit atual={open_profit:.2f} > 0 -> Fechando e travando lucro (preservando lucro diario)")
                                self.reset_cycle()
                                time.sleep(1)
                                continue
                        # Se houver lucro pequeno (ex.: $0.15) ou niveis baixos, ignora para evitar fechar em centavos
                        # Nota: removido log de status para evitar poluição do terminal; deixamos logs apenas quando o bot efetivamente fecha/resseta.
                except Exception:
                    logging.error("Erro ao processar fechamento por floating positivo")
                
                if account:
                    current_equity = account['equity']
                    
                    # Atualiza peak equity
                    if current_equity > self.peak_equity:
                        self.peak_equity = current_equity
                    
                    # Calcula drawdown (diferença entre peak e equity atual)
                    if self.peak_equity > 0:
                        current_drawdown = self.peak_equity - current_equity
                        if current_drawdown > self.max_drawdown:
                            self.max_drawdown = current_drawdown
                
                # Verifica se atingiu meta diaria
                if self.daily_profit >= self.daily_profit_target and not self.target_reached_today:
                    # META ATINGIDA! Fecha TODAS as posições
                    _cwarn("=" * 60)
                    _cwarn(f"[META ATINGIDA!!!] Lucro diario: ${self.daily_profit:.2f}")
                    _cwarn("[FECHANDO TODAS AS POSICOES]")
                    _cwarn("=" * 60)

                    # Fecha tudo
                    self.close_all_positions()
                    # Imprime FINAL BALANCE colorido ao fechar por meta atingida
                    try:
                        account_end = self.get_account_info()
                        if account_end:
                                # Calcula lucro diario atual
                                try:
                                    daily_end = self.get_daily_profit()
                                except Exception:
                                    daily_end = getattr(self, 'daily_profit', 0.0)
                                profit_end = account_end.get('profit', 0.0)
                                now = datetime.now()
                                ts = f"{now:%Y-%m-%d %H:%M:%S},{int(now.microsecond/1000):03d}"
                                print(f"{ts} ", end='')
                                print(Fore.CYAN + "------------------------------------------------------------" + Style.RESET_ALL)
                                print(f"{ts} ", end='')
                                print(Fore.GREEN + f"FINAL BALANCE: ${account_end['balance']:.2f} | EQUITY: ${account_end['equity']:.2f} | LUCRO_DIARIO: ${daily_end:.2f}" + Style.RESET_ALL)
                                print(f"{ts} ", end='')
                                print(Fore.CYAN + "------------------------------------------------------------" + Style.RESET_ALL)
                    except Exception:
                        pass
                    self.target_reached_today = True  # Marca que ja fechou hoje
                    _cinfo("[OK] Todas posicoes fechadas com sucesso!")
                    _cinfo("[OK] Esperando novo ciclo (aguardando reset configurado)")
                    _cinfo("=" * 60)

                elif self.target_reached_today:
                    # Ja atingiu meta hoje, apenas log ocasional
                    current_minute = int(time.time() / 14400)
                    if not hasattr(self, '_last_log_minute') or self._last_log_minute != current_minute:
                        _cinfo(f"[META ATINGIDA] Aguardando novo dia | Lucro final: ${self.daily_profit:.2f}")
                        self._last_log_minute = current_minute
                else:
                    # Nao atingiu meta ainda, continua abrindo
                    self.check_and_open_grid_levels()
                
                # Aguarda antes de proxima verificacao
                time.sleep(5)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                logging.error(f"Erro no loop: {e}")
                time.sleep(5)
        
        _cwarn("[STOP] Bot parado")
