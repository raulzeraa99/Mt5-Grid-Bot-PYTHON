# 🌐 Dashboard Web - MT5 Scalper Bot

## 🎨 **Painel de Controle Completo no Navegador!**

Dashboard web em tempo real para monitorar e controlar o bot.

---

## ✨ **Funcionalidades**

### 📊 **Monitoramento em Tempo Real:**
- Balance e Equity atualizados a cada 2 segundos
- Lucro/prejuízo do dia
- Número de trades executados
- Indicador visual de status (online/offline)

### 📍 **Gestão de Posições:**
- Lista de todas as posições abertas
- Lucro/prejuízo de cada posição em tempo real
- **Fechar posições manualmente** com um clique
- Informações detalhadas (SL, TP, preço de entrada, etc.)

### ✍️ **Abrir Trades Manualmente:**
- Interface intuitiva para abrir posições
- Configurar símbolo, tipo (BUY/SELL), lote, SL e TP
- Execução instantânea

### 📈 **Dados de Mercado:**
- Preços Bid/Ask em tempo real
- RSI, ATR e indicadores técnicos
- Estrutura de mercado (UPTREND/DOWNTREND/SIDEWAYS)
- Spread atual

### 📜 **Histórico de Trades:**
- Todos os trades do dia
- Lucro/prejuízo de cada operação
- Horário de execução

### 📝 **Logs em Tempo Real:**
- Últimas 50 linhas do log
- Atualização automática
- Scroll automático

---

## 🚀 **Como Usar**

### **1. Instalar Dependências:**

```bash
pip install -r requirements.txt
```

Isso instala Flask e Flask-CORS além das dependências do bot.

### **2. Configurar Credenciais:**

Edite `run_bot_with_dashboard.py`:

```python
# Login Automático (RECOMENDADO!)
USE_AUTO_LOGIN = True

MT5_LOGIN = 12345678              # SEU número
MT5_PASSWORD = "sua_senha"        # SUA senha
MT5_SERVER = "MetaQuotes-Demo"    # SEU servidor
```

### **3. Executar o Bot + Dashboard:**

```bash
python run_bot_with_dashboard.py
```

### **4. Acessar o Dashboard:**

O navegador abrirá automaticamente em:
```
http://localhost:5000
```

Se não abrir, digite manualmente no navegador!

---

## 📱 **Interface do Dashboard**

### **Topo - Cards de Status:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 💰 Balance  │ 📊 Equity   │ 💵 Lucro    │ 📈 Trades   │
│ R$ 10.000   │ R$ 10.250   │ R$ 250,00   │ 5 / 20      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### **Posições Abertas:**
```
Ticket  | Símbolo | Tipo | Volume | Preço | SL  | TP  | Lucro  | Ação
---------------------------------------------------------------------
123456  | XAUUSD  | BUY  | 0.10   | 1950  | ... | ... | +R$50  | [Fechar]
```

### **Abrir Trade Manual:**
```
┌────────────┬────────────┬────────┬────────┬────────┬──────────────┐
│ Símbolo ▼  │ Tipo ▼     │ Lote   │ SL     │ TP     │ [🚀 Abrir]   │
│ XAUUSD     │ COMPRA     │ 0.01   │ 100    │ 200    │              │
└────────────┴────────────┴────────┴────────┴────────┴──────────────┘
```

---

## 🎯 **Casos de Uso**

### **1. Monitoramento Básico:**
- Deixe o bot rodando
- Abra o dashboard no celular/tablet/PC
- Acompanhe em tempo real

### **2. Intervenção Manual:**
- Bot detecta sinal mas você quer confirmar
- Verifique dados de mercado no dashboard
- Decida se abre manualmente ou deixa o bot

### **3. Gestão de Risco:**
- Vê que posição está indo mal
- Fecha manualmente antes de bater SL
- Ou fecha no lucro antes do TP

### **4. Operação Híbrida:**
- Bot opera automaticamente
- Você abre trades adicionais manualmente
- Melhor dos dois mundos!

---

## 🔧 **Configurações Avançadas**

### **Mudar Porta do Servidor:**

Em `run_bot_with_dashboard.py`:

```python
DASHBOARD_PORT = 8080  # Porta personalizada
```

Acesse em: `http://localhost:8080`

### **Acessar de Outro Dispositivo (mesma rede):**

1. Descubra o IP do seu PC:
   ```bash
   ipconfig
   ```
   Procure por "IPv4" (ex: 192.168.1.100)

2. No celular/tablet, acesse:
   ```
   http://192.168.1.100:5000
   ```

### **Rodar em VPS (servidor remoto):**

Dashboard já está configurado para aceitar conexões externas (`host='0.0.0.0'`).

No VPS:
1. Execute o bot normalmente
2. Configure firewall para liberar porta 5000
3. Acesse via IP público: `http://SEU_IP:5000`

**⚠️ IMPORTANTE:** Configure senha/autenticação antes de expor na internet!

---

## 🛡️ **Segurança**

### **⚠️ Dashboard NÃO tem autenticação por padrão!**

Qualquer pessoa que acessar `http://localhost:5000` terá controle total.

### **Recomendações:**

1. **Uso Local:** OK sem senha
2. **Rede Local:** Configure firewall
3. **Internet Pública:** 
   - Adicione autenticação (Flask-Login)
   - Use HTTPS
   - Configure senha forte
   - Limite acesso por IP

---

## 🐛 **Problemas Comuns**

### **Erro: "Address already in use"**

Porta 5000 já está em uso.

**Solução:**
```python
DASHBOARD_PORT = 8080  # Mude para outra porta
```

### **Dashboard não abre automaticamente**

Abra manualmente: `http://localhost:5000`

### **Erro: "Module Flask not found"**

Instale as dependências:
```bash
pip install Flask Flask-CORS
```

### **Dados não atualizam**

1. Verifique se o bot está rodando
2. Veja o console do navegador (F12)
3. Confira se há erros no terminal do bot

---

## 📊 **Roadmap / Melhorias Futuras**

Possíveis adições:

- [ ] Gráficos interativos com Chart.js
- [ ] Notificações push quando abrir/fechar trades
- [ ] Autenticação com senha
- [ ] Múltiplos usuários
- [ ] Modo escuro
- [ ] Exportar relatórios em PDF
- [ ] Integração com Telegram
- [ ] Alertas sonoros
- [ ] Análise de performance (Sharpe, Sortino)
- [ ] Otimizador de parâmetros

---

## 💡 **Dicas**

1. **Deixe em tela cheia no segundo monitor** para monitoramento constante
2. **Use no celular** para acompanhar de qualquer lugar (mesma rede)
3. **Abra em múltiplas abas** para ver diferentes seções
4. **Configure alertas no navegador** (se implementar)

---

## 🎨 **Personalização**

### **Mudar Cores:**

Edite `templates/dashboard.html` na seção `<style>`:

```css
/* Muda cor principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    ↑ Sua cor aqui
```

### **Mudar Frequência de Atualização:**

No final do HTML:

```javascript
setInterval(updateDashboard, 5000);  // Atualiza a cada 5 segundos
                              ↑
                        Milissegundos
```

---

## 📞 **Suporte**

Se tiver problemas:

1. Veja o console do navegador (F12 > Console)
2. Veja o terminal do bot (erros aparecem lá)
3. Confira `logs/mt5_scalper.log`

---

## ⚖️ **Disclaimer**

O dashboard permite abrir e fechar trades manualmente.

**⚠️ USE COM CUIDADO!**

- Trades manuais ignoram filtros do bot
- Você assume total responsabilidade
- Teste em demo antes de usar em conta real

---

**Aproveite seu dashboard! 🚀📊**
