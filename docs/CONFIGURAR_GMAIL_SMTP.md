# 📧 Como Configurar Gmail SMTP para Notificações

## ✅ Pré-requisito: Ativar Verificação em Duas Etapas

1. Acesse: https://myaccount.google.com/security
2. Procure por **"Verificação em duas etapas"**
3. Clique em **"Começar"** e siga as instruções
4. ⚠️ **É OBRIGATÓRIO** ter verificação em duas etapas ativada

## 🔑 Criar Senha de App

### Opção 1: Link Direto
1. Acesse diretamente: https://myaccount.google.com/apppasswords
2. Se necessário, faça login

### Opção 2: Via Menu
1. Acesse: https://myaccount.google.com/
2. Clique em **"Segurança"** (lateral esquerda)
3. Procure por **"Senhas de app"**
4. Clique em **"Senhas de app"**

## 📝 Configuração da Senha

1. Em **"Selecione o app"**, escolha:
   - **"E-mail"** OU
   - **"Outro (nome personalizado)"** → Digite: `PGR Sistema`

2. Em **"Selecione o dispositivo"**, escolha:
   - **"Outro (nome personalizado)"** → Digite: `Railway` ou `Produção`

3. Clique em **"Gerar"**

4. **Uma senha de 16 caracteres será exibida:**
   ```
   abcd efgh ijkl mnop
   ```

5. **Copie essa senha** (você não poderá vê-la novamente!)

## 🔧 Configurar no Railway

No painel do Railway, adicione as variáveis:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

⚠️ **Importante:**
- Use a senha de 16 caracteres **sem espaços**
- Não use sua senha normal do Gmail
- A senha de app é específica para este uso

## ✅ Testar Configuração

Depois de configurar, você pode testar enviando um email através da API:

```bash
curl -X POST https://seu-app.up.railway.app/api/notifications/send \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "destinatario@exemplo.com",
    "subject": "Teste",
    "body": "Email de teste do sistema PGR"
  }'
```

## 🛠️ Solução de Problemas

### Erro: "Bad credentials"
- Verifique se está usando a senha de app (16 caracteres), não a senha normal
- Confirme que a verificação em duas etapas está ativada

### Erro: "Less secure app access"
- Google não permite mais "apps menos seguros"
- Use senha de app (não precisa habilitar apps menos seguros)

### Erro: "Connection refused"
- Verifique `SMTP_HOST` e `SMTP_PORT`
- Gmail usa: `smtp.gmail.com:587`

### Não consigo ver "Senhas de app"
- Confirme que a verificação em duas etapas está **ativada**
- Tente acessar diretamente: https://myaccount.google.com/apppasswords
- Use uma conta Google pessoal (não corporativa - contas corporativas podem ter políticas diferentes)

## 🔒 Segurança

- ✅ Senhas de app são mais seguras que senhas normais
- ✅ Você pode revogar uma senha de app a qualquer momento
- ✅ Cada app/device tem sua própria senha
- ✅ Se suspeitar de comprometimento, revogue e crie uma nova

## 📚 Alternativas ao Gmail

Se preferir outro provedor:

### Outlook/Hotmail
```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu-email@outlook.com
SMTP_PASSWORD=sua-senha-normal
```

### SendGrid (Recomendado para produção)
1. Crie conta em: https://sendgrid.com
2. Crie API Key
3. Use:
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=sua-api-key-aqui
```

### Mailgun
```
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=seu-usuario@mailgun
SMTP_PASSWORD=sua-senha-mailgun
```

---

**Última atualização:** Dezembro 2025

