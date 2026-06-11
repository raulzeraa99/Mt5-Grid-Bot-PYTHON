"""
Executa o MT5 Grid Bot com Martingale
Configuracao: XAUUSDm, mesma conta do scalper
"""

from mt5_grid_bot import MT5GridBot
import time

# ==================================================
# CONFIGURACAO - EDITE AQUI!
# ==================================================

# Login (mesma conta do scalper)
MT5_LOGIN = "LOGIN MT5"
MT5_PASSWORD = "SENHA AQUI"
MT5_SERVER = "SERVIDOR DA CONTA AQUI"

# Configuracoes do Grid
SYMBOL = 'XAUUSDm'              # Simbolo para operar
GRID_DISTANCE = 500             # Distancia entre niveis (em pontos)
INITIAL_LOT = 0.01              # Lote inicial
PROFIT_TARGET = 100.0           # Meta de lucro ($) para fechar TUDO
MAX_LEVELS = 30                 # Maximo de niveis de grid (permite 30 BUY + 30 SELL)

# ==================================================

def main():
    print("=" * 60)
    print(">> MT5 GRID BOT COM MARTINGALE")
    print("=" * 60)
    print()
    
    # Cria o bot
    print(">> Criando Grid Bot...")
    bot = MT5GridBot(
        symbol=SYMBOL,
        grid_distance=GRID_DISTANCE,
        initial_lot=INITIAL_LOT,
        daily_profit_target=PROFIT_TARGET,
        max_levels=MAX_LEVELS
    )
    
    print(f"   Simbolo: {SYMBOL}")
    print(f"   Distancia Grid: {GRID_DISTANCE} pontos")
    print(f"   Lote Inicial: {INITIAL_LOT}")
    print(f"   Meta de Lucro: ${PROFIT_TARGET:.2f}")
    print(f"   Max Niveis: {MAX_LEVELS}")
    print()
    
    # Inicializa MT5
    print(">> Conectando ao MT5...")
    print(f"   Fazendo login na conta {MT5_LOGIN}...")
    
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
    
    print("[OK] MT5 conectado com sucesso!")
    print()
    
    # RESET MANUAL - Zera tudo para recomeçar
    print(">> Resetando contadores (recomeçando do zero)...")
    bot.reset_now()
    print()
    
    print("=" * 60)
    print("[OK] GRID BOT INICIADO COM SUCESSO!")
    print("=" * 60)
    print()
    print(">> COMO FUNCIONA:")
    print("1. Abre posicoes em grid (distancia de", GRID_DISTANCE, "pontos)")
    print("2. Dobra o lote a cada novo nivel (Martingale)")
    print("3. Quando LUCRO DIARIO atingir $", PROFIT_TARGET)
    print("   -> PARA de abrir novas posicoes (NAO fecha as abertas)")
    print("4. Reset a meia-noite para comecar novo dia")
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
        print("[OK] Bot encerrado com sucesso!")

if __name__ == "__main__":
    main()
