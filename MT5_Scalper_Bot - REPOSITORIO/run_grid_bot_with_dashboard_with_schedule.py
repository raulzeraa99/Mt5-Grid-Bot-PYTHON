"""
Executa o MT5 Grid Bot com Dashboard Web
Abre automaticamente o navegador com a interface de controle
"""

import threading
import webbrowser
import time
from datetime import datetime
from mt5_grid_bot_with_schedule import MT5GridBot, Fore, Style
from dashboard_grid import set_bot_instance, run_dashboard

# ==================================================
# CONFIGURACAO - EDITE AQUI!
# ==================================================

# Login (mesma conta do scalper)
MT5_LOGIN = "LOGIN MT5"
MT5_PASSWORD = "SENHA AQUI"
MT5_SERVER = "SERVIDOR DA CONTA AQUI"

# Configuracoes do Grid
SYMBOL = 'XAUUSDm'              # Simbolo para operar
GRID_DISTANCE = 1500            # Distancia entre niveis (em pontos) - atualizado
TAKE_PROFIT = 1000              # Take profit em pontos
INITIAL_LOT = 0.01              # Lote inicial
PROFIT_TARGET = 100.0           # Meta de lucro ($) para fechar TUDO
MAX_LEVELS = 10                 # Maximo de niveis de grid (ajustado para 10)

# Dashboard
DASHBOARD_PORT = 5001           # Porta diferente do scalper (5000)

# ==================================================

def main():
    print("=" * 60)
    print(">> MT5 GRID BOT COM MARTINGALE + DASHBOARD")
    print("=" * 60)
    print()
    
    # Cria o bot
    print(">> Criando Grid Bot...")
    # Sequencia de lotes personalizada (10 levels). Ajuste se quiser outros valores.
    lot_schedule = [0.01, 0.03, 0.06, 0.12, 0.24, 0.48, 0.96, 1.92, 3.84, 7.68]

    bot = MT5GridBot(
        symbol=SYMBOL,
        grid_distance=GRID_DISTANCE,
        initial_lot=INITIAL_LOT,
        daily_profit_target=PROFIT_TARGET,
        max_levels=MAX_LEVELS,
        take_profit_points=TAKE_PROFIT,
        reset_hour=20,
        reset_minute=30
        , lot_schedule=lot_schedule
    )
    # DEBUG: confirma qual lot_schedule a instancia recebeu e de qual arquivo a classe veio
    try:
        import inspect, sys
        print("DEBUG: bot.lot_schedule:", bot.lot_schedule)
        mod = sys.modules.get(MT5GridBot.__module__)
        print("DEBUG: MT5GridBot source:", getattr(mod, '__file__', MT5GridBot.__module__))
    except Exception:
        pass
    
    print(f"   Simbolo: {SYMBOL}")
    print(f"   Distancia Grid: {GRID_DISTANCE} pontos")
    print(f"   Lote Inicial: {INITIAL_LOT}")
    print(f"   Meta de Lucro: ${PROFIT_TARGET:.2f}")
    print(f"   Max Niveis: {MAX_LEVELS}")
    print()
    
    # Inicializa MT5
    print(">> Conectando ao MT5...")
    #print(f"   Fazendo login na conta {MT5_LOGIN}...")
    
    success = bot.initialize(
        login=MT5_LOGIN,
        password=MT5_PASSWORD,
        server=MT5_SERVER
    )
    
    if not success:
        print()
        print("[ERRO] Nao foi possivel inicializar o bot!")
        print()
        print("DICAS:")
        print("1. Verifique se o MT5 esta instalado")
        print("2. Confira as credenciais")
        print("3. Certifique-se que AutoTrading esta habilitado")
        return
    
    print(Fore.GREEN + f"[OK] MT5 conectado com sucesso!" + Style.RESET_ALL)
    print()
    # Exibe balance/equity logo apos conectar ao MT5
    try:
        account = bot.get_account_info()
        # Informacoes da conta com cor e timestamp
        if account:
            print(Fore.CYAN + "------------------------------------------------------------" + Style.RESET_ALL)
            print(Fore.GREEN + f"VALOR BALANCE: ${account['balance']:.2f} | EQUITY: ${account['equity']:.2f}" + Style.RESET_ALL)
            print(Fore.CYAN + "------------------------------------------------------------" + Style.RESET_ALL)
        else:
            print(Fore.RED + "[ERRO] Nao foi possivel obter informacoes da conta" + Style.RESET_ALL)
    except Exception as e:
        print(f"[ERRO] Falha ao obter informacoes da conta: {e}")
    
    # RESET MANUAL - Zera tudo para recomeçar
    print(">> Resetando contadores (recomeçando do zero)...")
    bot.reset_now()
    print()
    
    # Configura dashboard
    print(">> Iniciando dashboard web...")
    set_bot_instance(bot)
    
    # Inicia dashboard em thread separada
    dashboard_thread = threading.Thread(
        target=run_dashboard,
        kwargs={'host': '0.0.0.0', 'port': DASHBOARD_PORT},
        daemon=True
    )
    dashboard_thread.start()
    
    # Aguarda servidor iniciar
    time.sleep(2)
    
    print(f"[OK] Dashboard rodando em: http://localhost:{DASHBOARD_PORT}")
    print()
    print(">> Abrindo navegador...")
    
    # Abre navegador
    webbrowser.open(f'http://localhost:{DASHBOARD_PORT}')
    
    print()
    print("=" * 60)
    print(Fore.GREEN + f"[OK] GRID BOT INICIADO COM SUCESSO!" + Style.RESET_ALL)
    print("=" * 60)
    print()
    print(f">> Acesse o dashboard em: http://localhost:{DASHBOARD_PORT}")
    #print("   (O navegador deve abrir automaticamente)")
    print()
    print("[AVISO] Para parar o bot, pressione Ctrl+C")
    print()
    print("=" * 60)
    print()
    
    # Roda o bot
    try:
        bot.run()
    except KeyboardInterrupt:
        print()
        print("[STOP] Bot interrompido pelo usuario")
    finally:
        print(">> Desconectando MT5...")
        bot.shutdown()
        print(Fore.GREEN + f"[OK] Bot encerrado com sucesso!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
