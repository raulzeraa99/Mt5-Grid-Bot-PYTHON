# MT5 Scalper Bot - Configuração e Uso

## 📋 Pré-requisitos

1. **MetaTrader 5 instalado** no Windows
2. **Python 3.8+** instalado
3. **Conta demo ou real** na corretora

## 🚀 Instalação

```bash
pip install -r requirements_mt5.txt
```

## ⚙️ Configuração

### 1. Ajustar Símbolos
Verifique na sua corretora a nomenclatura correta:
- **Ouro**: pode ser `XAUUSD`, `GOLD`, `XAUUSD.a`, etc.
- **Nasdaq**: pode ser `NAS100`, `US100`, `USTEC`, etc.

Ajuste na linha 287 do arquivo:
```python
symbols=['XAUUSD', 'NAS100']
```

### 2. Parâmetros Importantes

No arquivo `mt5_scalper_bot.py`, você pode ajustar:

**Gerenciamento de Risco (linhas 34-37):**
```python
self.risk_percent = 1.0          # % do capital por trade
self.max_daily_loss = 3.0        # % máximo de perda no dia
self.max_trades_per_day = 20     # Número máximo de trades/dia
```

**Horário de Operação (linhas 39-42):**
```python
self.start_hour = 9              # Hora início
self.start_minute = 0
self.end_hour = 17               # Hora fim
self.end_minute = 30
```

**Stop Loss e Take Profit (linhas 44-48):**
```python
self.sl_tp_config = {
    'XAUUSD': {'sl': 50, 'tp': 100, 'trailing': 30},
    'NAS100': {'sl': 80, 'tp': 150, 'trailing': 50}
}
```

**Indicadores (linhas 25-30):**
```python
self.ema_fast = 9                # EMA rápida
self.ema_slow = 21               # EMA lenta
self.rsi_period = 14             # Período RSI
```

## 🎯 Como Usar

### 1. Abra o MetaTrader 5
- Faça login na sua conta
- Deixe o MT5 aberto e rodando

### 2. Execute o Bot
```bash
python mt5_scalper_bot.py
```

### 3. Monitoramento
O bot criará um arquivo `mt5_scalper.log` com todas as operações.

## 📊 Estratégia

### Sinais de Entrada

**COMPRA:**
- EMA rápida cruza acima da EMA lenta
- RSI entre 40-60 (evita sobrecompra)
- Volume acima da média

**VENDA:**
- EMA rápida cruza abaixo da EMA lenta
- RSI entre 40-60 (evita sobrevenda)
- Volume acima da média

### Gestão de Posição
- **1 posição por símbolo** por vez
- **Trailing Stop** automático para proteger lucros
- **Stop Loss** e **Take Profit** fixos por símbolo
- **Fechamento automático** ao atingir targets

### Proteções
- Limite de trades diários
- Stop loss do dia (perda máxima)
- Horário de operação definido
- Tamanho de lote baseado em risco %

## ⚠️ Avisos Importantes

1. **Teste em CONTA DEMO primeiro!**
2. **Não garante lucros** - mercado tem risco inerente
3. **Monitore o bot** regularmente
4. **Ajuste parâmetros** após backtests
5. **Use VPS** para operação 24/7 sem interrupções

## 🔧 Otimização

Para melhorar resultados:

1. **Backtest**: Teste a estratégia com dados históricos
2. **Ajuste SL/TP**: Baseado na volatilidade de cada ativo
3. **Timeframe**: Teste M1 para scalping mais agressivo
4. **Filtros**: Adicione filtros de tendência (ADX, MACD)
5. **Horários**: Opere apenas nos horários de maior liquidez

## 📈 Exemplo de Uso

```python
# Configuração conservadora
bot = MT5ScalperBot(
    symbols=['XAUUSD'],
    timeframe=mt5.TIMEFRAME_M5
)
bot.risk_percent = 0.5        # Apenas 0.5% de risco
bot.max_trades_per_day = 10   # Máximo 10 trades
```

```python
# Configuração agressiva
bot = MT5ScalperBot(
    symbols=['XAUUSD', 'NAS100'],
    timeframe=mt5.TIMEFRAME_M1
)
bot.risk_percent = 2.0        # 2% de risco
bot.max_trades_per_day = 30   # Até 30 trades
```

## 📝 Logs

O bot registra:
- ✓ Todas as operações (abertura/fechamento)
- ✓ Sinais detectados
- ✓ Erros e avisos
- ✓ Lucro/prejuízo diário
- ✓ Status da conta

## 🛑 Para Parar o Bot

Pressione `Ctrl + C` no terminal.

## 💡 Dicas

1. **Capital mínimo recomendado**: R$ 5.000 - R$ 10.000
2. **Risco por trade**: Não exceda 2% do capital
3. **Diversifique**: Não opere apenas 1 ativo
4. **Revise diariamente**: Analise os logs e resultados
5. **Disciplina**: Respeite os limites de perda

## 🔄 Próximos Passos

1. Testar em demo por pelo menos 1 mês
2. Ajustar parâmetros baseado nos resultados
3. Implementar backtesting automatizado
4. Adicionar mais filtros de entrada
5. Criar dashboard de monitoramento

---

**⚠️ DISCLAIMER**: Trading envolve risco. Opere com capital que pode perder. Este bot é apenas uma ferramenta - você é responsável pelos resultados.
