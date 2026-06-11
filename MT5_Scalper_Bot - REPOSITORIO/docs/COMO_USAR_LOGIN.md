# 🔐 Como Configurar Login no MT5 Scalper Bot

## 📋 Existem 2 formas de usar o bot:

---

## ✅ **OPÇÃO 1: Login Manual (RECOMENDADO)**

### Mais Seguro e Simples!

**Passo a passo:**

1. **Abra o MetaTrader 5**
   - Dê duplo clique no ícone do MT5

2. **Faça Login Normalmente**
   - Vá em: `Arquivo > Login em Conta de Negociação`
   - Digite: Conta, Senha, Servidor
   - Clique em OK

3. **Deixe o MT5 Aberto**
   - NÃO feche o MT5!

4. **Execute o Bot**
   ```bash
   python mt5_grid_bot.py
   ```

O bot detecta automaticamente que o MT5 está logado e se conecta! ✨

**Vantagens:**
- ✅ Mais seguro (senha não fica no código)
- ✅ Mais simples
- ✅ Recomendado para iniciantes
- ✅ Funciona em demo e real

---

## 🔧 **OPÇÃO 2: Login Automático via Código**

### Para Usuários Avançados / VPS

Use quando:
- Rodar em VPS sem interface gráfica
- Automação total
- Múltiplas contas

### **Método A: Editar o Arquivo Principal**

Edite `mt5_grid_bot.py` no final:

```python
if __name__ == "__main__":
    bot = MT5SgridBot(
        symbols=['XAUUSD', 'NAS100'],
        timeframe=mt5.TIMEFRAME_M5
    )
    
    # DESCOMENTE e PREENCHA:
    CONTA = 12345678                  # Seu número de conta
    SENHA = "sua_senha"               # Sua senha
    SERVIDOR = "MetaQuotes-Demo"      # Servidor da corretora
    
    if bot.initialize(login=CONTA, password=SENHA, server=SERVIDOR):
        try:
            bot.run()
        finally:
            bot.shutdown()
```

### **Método B: Usar Arquivo de Configuração (MAIS SEGURO)**

1. **Configure suas credenciais:**

Edite `config/credentials.py`:

```python
# Ative o login automático
USE_AUTO_LOGIN = True

# Suas credenciais
MT5_LOGIN = 12345678              # Número da conta
MT5_PASSWORD = "sua_senha_real"   # Senha
MT5_SERVER = "MetaQuotes-Demo"    # Servidor
```

2. **Execute usando o script especial:**

```bash
python run_bot.py
```

Pronto! O bot fará login automaticamente.

---

## 🔍 **Como Descobrir Suas Informações?**

### **1. Número da Conta**
No MT5, veja no topo da janela:
```
MetaTrader 5 - 12345678 - MetaQuotes-Demo
              ^^^^^^^^ (este é o número)
```

### **2. Servidor**
No MT5:
- `Ferramentas > Opções > Servidor`
- Ou na janela de login

**Exemplos comuns:**
- `MetaQuotes-Demo` (demo MetaQuotes)
- `XPInvestimentos-Demo`
- `XM-Demo` / `XM-Real`
- `FXCM-Demo`
- `Ativa-Demo`
- etc.

### **3. Senha**
É a senha que você criou ao abrir a conta!

---

## ⚠️ **SEGURANÇA IMPORTANTE**

### **Se usar login automático:**

1. **NUNCA compartilhe arquivos com credenciais!**
2. **Não envie para GitHub/Git:**
   
   Crie arquivo `.gitignore`:
   ```
   config/credentials.py
   *.log
   ```

3. **Em VPS/Produção, use variáveis de ambiente:**

```python
import os

MT5_LOGIN = int(os.getenv('MT5_LOGIN'))
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_SERVER = os.getenv('MT5_SERVER')
```

No Windows (VPS):
```bash
setx MT5_LOGIN "12345678"
setx MT5_PASSWORD "sua_senha"
setx MT5_SERVER "MetaQuotes-Demo"
```

---

## 🐛 **Problemas Comuns**

### **Erro: "Falha ao inicializar MT5"**

**Solução:**
- ✓ MT5 está instalado?
- ✓ MT5 está aberto? (se usar login manual)
- ✓ Credenciais estão corretas? (se usar login automático)

### **Erro: "Falha ao fazer login"**

**Possíveis causas:**
1. **Número da conta errado**
   - Verifique no MT5
2. **Senha incorreta**
   - Teste fazendo login manual primeiro
3. **Servidor errado**
   - Veja nome EXATO em Ferramentas > Opções > Servidor
4. **Conta expirou** (demo)
   - Contas demo expiram após 30 dias
   - Abra uma nova conta demo

### **Erro: "Unauthorized"**

Significa que a senha está errada.

**Solução:**
1. Tente fazer login manual no MT5 primeiro
2. Se funcionar manual mas não automático:
   - Copie e cole a senha (evita erros de digitação)
   - Verifique espaços em branco na senha

---

## 📝 **Exemplos Práticos**

### **Exemplo 1: Conta Demo XP**

```python
CONTA = 87654321
SENHA = "minhasenha123"
SERVIDOR = "XPInvestimentos-Demo"

bot.initialize(login=CONTA, password=SENHA, server=SERVIDOR)
```

### **Exemplo 2: Conta Real (CUIDADO!)**

```python
CONTA = 12345678
SENHA = "senhasegura@2026"
SERVIDOR = "XM-Real"

bot.initialize(login=CONTA, password=SENHA, server=SERVIDOR)
```

⚠️ **Teste SEMPRE em demo primeiro!**

---

## 🎯 **Recomendação Final**

Para 99% dos usuários:

**Use OPÇÃO 1 (Login Manual)**
- Mais simples
- Mais seguro
- Menos dor de cabeça

Só use login automático se:
- Rodar em VPS
- Precisa de automação total
- Sabe o que está fazendo

---

## 💡 **Dica Profissional**

Se usar VPS (servidor remoto):

1. Configure variáveis de ambiente
2. Use autenticação de dois fatores (se disponível)
3. Troque a senha regularmente
4. Monitore acessos suspeitos

---

**Precisa de ajuda?**

1. Leia este documento novamente
2. Execute `python validar_bot.py` para diagnóstico
3. Verifique os logs em `logs/mt5_scalper.log`
