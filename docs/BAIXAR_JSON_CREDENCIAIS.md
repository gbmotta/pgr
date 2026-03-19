# Como Baixar o JSON de Credenciais do Service Account

## Passo a Passo Detalhado

### 1. Acessar a Service Account

1. No Google Cloud Console, você já está na página de IAM
2. No menu lateral esquerdo, clique em **"Contas de serviço"** (Service Accounts)
3. Você verá a lista de Service Accounts do projeto

### 2. Abrir a Service Account Específica

1. Na lista, encontre e clique na Service Account: **`gmottaz`**
   - Email: `gmottaz@dashboard-matriarca.iam.gserviceaccount.com`
2. Isso abrirá a página de detalhes da Service Account

### 3. Criar e Baixar a Chave JSON

1. Na página de detalhes da Service Account, procure a aba **"Keys"** (Chaves) ou **"Chaves"**
2. Clique em **"Add Key"** (Adicionar chave) ou **"Criar chave"**
3. Selecione **"Create new key"** (Criar nova chave)
4. Escolha o formato: **JSON**
5. Clique em **"Create"** (Criar)
6. O arquivo JSON será baixado automaticamente para sua pasta de Downloads

### 4. Verificar o Arquivo Baixado

O arquivo terá um nome como:
- `dashboard-matriarca-xxxxx-xxxxx.json` (nome automático do Google)
- Ou outro nome gerado automaticamente

### 5. Mover e Renomear o Arquivo

1. Abra o terminal e execute:

```bash
# Verificar se o arquivo foi baixado
ls -la ~/Downloads/*.json

# Mover e renomear para o local correto
mv ~/Downloads/dashboard-matriarca-*.json /home/gab/Documentos/PGR/credentials/service_account.json
```

Ou manualmente:
1. Vá para sua pasta de Downloads
2. Encontre o arquivo JSON baixado
3. Renomeie para `service_account.json`
4. Mova para: `/home/gab/Documentos/PGR/credentials/`

### 6. Verificar se Está Correto

O arquivo JSON deve conter algo como:

```json
{
  "type": "service_account",
  "project_id": "dashboard-matriarca",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "gmottaz@dashboard-matriarca.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

**Importante:** Verifique se o campo `client_email` corresponde ao email que você encontrou!

### 7. Testar no Sistema

Depois de colocar o arquivo, reinicie o servidor e teste:

```bash
# Verificar se o arquivo está no lugar certo
ls -la /home/gab/Documentos/PGR/credentials/service_account.json

# Testar se o sistema consegue ler
python3 -c "from backend import google_auth; print('Email:', google_auth.get_service_account_email())"
```

## Resumo Visual

```
Google Cloud Console
  └─ IAM & Admin
      └─ Service Accounts (Contas de serviço)
          └─ gmottaz (clique aqui)
              └─ Aba "Keys" (Chaves)
                  └─ Add Key (Adicionar chave)
                      └─ Create new key (Criar nova chave)
                          └─ JSON (selecionar)
                              └─ Create (Criar)
                                  └─ Download automático
                                      └─ Mover para: credentials/service_account.json
```

## Localização Final do Arquivo

```
/home/gab/Documentos/PGR/
  └─ credentials/
      └─ service_account.json  ← Arquivo deve estar aqui
```

## Próximos Passos

Depois de baixar e colocar o arquivo:

1. ✅ O sistema carregará automaticamente o email
2. ✅ O email aparecerá na interface quando você acessar "Google Drive"
3. ✅ Você poderá compartilhar planilhas com: `gmottaz@dashboard-matriarca.iam.gserviceaccount.com`
