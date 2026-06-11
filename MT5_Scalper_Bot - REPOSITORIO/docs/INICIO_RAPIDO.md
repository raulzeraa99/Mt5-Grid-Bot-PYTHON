# 🚀 GUIA RÁPIDO - MT5 Scalper Bot

## 📦 Instalação Rápida

### 1. Instalar Dependências
```bash
pip install -r requirements_mt5.txt
```

### 2. Verificar Símbolos
Abra o MT5 e verifique a nomenclatura dos ativos:
- **Ouro**: Procure por "gold" ou "xau"
- **Nasdaq**: Procure por "nas" ou "us100"

Anote o nome EXATO (exemplo: `XAUUSD`, `NAS100`, `GOLD.a`, etc.)

### 3. Ajustar Configuração
Edite o arquivo `mt5_scalper_bot.py` linha 287:
```python
symbols=['XAUUSD', 'NAS100']  # Cole os nomes exatos aqui
```

---

## 🧪 PASSO 1: Fazer BACKTEST (OBRIGATÓRIO)

**ANTES de usar dinheiro real, teste a estratégia!**

```bash
python mt5_backtest.py
```

### Ajustar Backtest:
Edite `mt5_backtest.py` nas linhas 247-250:
```python
SYMBOL = 'XAUUSD'          # Símbolo a testar
INITIAL_BALANCE = 10000    # Capital inicial
RISK_PERCENT = 1.0         # % de risco
DAYS = 30                  # Dias de histórico
```

### Interpretar Resultados:
- ✅ **Taxa de Acerto > 50%**: Boa estratégia
- ✅ **Fator de Lucro > 1.5**: Lucros maiores que perdas
- ✅ **Drawdown < 20%**: Risco controlado
- ❌ **Drawdown > 30%**: Muito arriscado - ajustar parâmetros

---

## 🎯 PASSO 2: Testar em CONTA DEMO

### 1. Abrir Conta Demo
No MT5: `Arquivo > Abrir Conta > Conta Demo`

### 2. Ajustar Parâmetros
Edite `mt5_scalper_bot.py`:

```python
# RISCO (linhas 34-37)
self.risk_percent = 0.5          # COMECE COM 0.5%
self.max_daily_loss = 2.0        # Perda máxima 2%
self.max_trades_per_day = 10     # Limite de trades

# SL/TP (linhas 44-48)
self.sl_tp_config = {
    'XAUUSD': {'sl': 50, 'tp': 100, 'trailing': 30},
    'NAS100': {'sl': 80, 'tp': 150, 'trailing': 50}
}
```

### 3. Rodar Bot
```bash
python mt5_scalper_bot.py
```

### 4. Monitorar
- Deixe rodar por **PELO MENOS 1 SEMANA**
- Acompanhe o arquivo `mt5_scalper.log`
- Verifique resultados no MT5

---

## 💰 PASSO 3: Conta Real (Apenas se Demo foi Lucrativa)

### ⚠️ CHECKLIST ANTES DE USAR CONTA REAL:

- [ ] Testei backtest e resultados foram positivos
- [ ] Rodei em demo por NO MÍNIMO 1 semana
- [ ] Obtive lucro consistente em demo
- [ ] Entendo que posso perder dinheiro
- [ ] Tenho capital que posso perder sem afetar vida pessoal
- [ ] Capital mínimo de R$ 5.000

### Capital Recomendado:
- **R$ 5.000 - R$ 10.000**: Conservador (0.5% risco)
- **R$ 10.000 - R$ 50.000**: Moderado (1% risco)
- **R$ 50.000+**: Agressivo (1.5% risco)

### Configuração Conta Real:
```python
# MUITO CONSERVADOR (recomendado no início)
self.risk_percent = 0.3
self.max_daily_loss = 1.5
self.max_trades_per_day = 5
```

---

## 📊 Monitoramento Diário

### O que verificar TODOS os dias:

1. **Arquivo de Log**:
```bash
type mt5_scalper.log
```

2. **Métricas Importantes**:
   - Número de trades executados
   - Taxa de acerto (win rate)
   - Lucro/prejuízo diário
   - Drawdown atual

3. **Ações se der Errado**:
   - Prejuízo > 2% no dia → PARAR BOT
   - Taxa de acerto < 40% → REVISAR ESTRATÉGIA
   - Drawdown > 20% → REDUZIR RISCO

---

## 🔧 Ajustes Comuns

### Muitos Trades (scalping demais):
```python
self.timeframe = mt5.TIMEFRAME_M15  # Linha 19
self.rsi_overbought = 65            # Linha 30
self.rsi_oversold = 35              # Linha 31
```

### Poucos Trades:
```python
self.timeframe = mt5.TIMEFRAME_M1   # Linha 19
self.rsi_overbought = 75            # Linha 30
self.rsi_oversold = 25              # Linha 31
```

### Muitas Perdas:
```python
# Aumentar SL/TP
self.sl_tp_config = {
    'XAUUSD': {'sl': 70, 'tp': 140, 'trailing': 40},
}
```

### Lucro muito pequeno:
```python
# Aumentar TP
self.sl_tp_config = {
    'XAUUSD': {'sl': 50, 'tp': 150, 'trailing': 40},
}
```

---

## 🛑 Como Parar o Bot

Pressione: `Ctrl + C`

---

## ❓ Troubleshooting

### Erro: "Falha ao inicializar MT5"
- ✓ MT5 está aberto?
- ✓ Você está logado na conta?
- ✓ Reinstale: `pip install --upgrade MetaTrader5`

### Erro: "Símbolo não encontrado"
- ✓ Verifique nome exato do símbolo no MT5
- ✓ Símbolo está visível na "Observação de Mercado"?

### Não executa trades
- ✓ Está no horário de operação?
- ✓ Limite de trades diários atingido?
- ✓ Verifique os logs para sinais detectados

### Trades fecham muito rápido
- ✓ Aumentar SL/TP
- ✓ Reduzir trailing stop

---

## 📈 Metas Realistas

### ❌ NÃO ESPERE:
- R$ 500/dia garantidos
- 100% de taxa de acerto
- Lucro todos os dias
- Ficar rico rápido

### ✅ ESPERE:
- 50-60% de taxa de acerto
- Dias com lucro e dias com perda
- Lucro de 3-8% ao mês (se tudo der certo)
- Necessidade de ajustes constantes
- Aprendizado contínuo

---

## 📞 Próximos Passos

1. ✅ Instalar dependências
2. ✅ Fazer backtest
3. ✅ Testar em demo (1 semana)
4. ✅ Ajustar parâmetros
5. ✅ Analisar resultados
6. ⏸️ **PARAR e PENSAR** antes de conta real
7. 💰 Conta real (APENAS se demo lucrou)

---

## ⚠️ AVISO FINAL

**TRADING É ARRISCADO. VOCÊ PODE PERDER TODO SEU DINHEIRO.**

Este bot é uma FERRAMENTA, não uma máquina de dinheiro.
Você é 100% RESPONSÁVEL pelos resultados.

**NÃO opere com dinheiro que você não pode perder!**
