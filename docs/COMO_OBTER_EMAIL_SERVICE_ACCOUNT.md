# Como Obter o Email do Service Account

## Onde está o email?

O email do Service Account está dentro do arquivo JSON de credenciais que você baixa do Google Cloud Console.

## Passo a Passo

### 1. Criar Service Account no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Selecione ou crie um projeto
3. Vá em **IAM & Admin** > **Service Accounts**
4. Clique em **Create Service Account**
5. Preencha:
   - **Name**: `pgr-sheets-service` (ou qualquer nome)
   - **Description**: "Service Account para integração com Google Sheets"
6. Clique em **Create and Continue**
7. Em **Grant this service account access to project**, adicione a role:
   - **Service Account User**
8. Clique em **Done**

### 2. Baixar Credenciais (JSON)

1. Na lista de Service Accounts, clique no que você criou
2. Vá na aba **Keys**
3. Clique em **Add Key** > **Create new key**
4. Selecione **JSON**
5. Clique em **Create**
6. O arquivo JSON será baixado automaticamente

### 3. Encontrar o Email no Arquivo JSON

Abra o arquivo JSON baixado. Você verá algo assim:

```json
{
  "type": "service_account",
  "project_id": "seu-projeto",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "pgr-sheets-service@seu-projeto.iam.gserviceaccount.com",
  "client_id": "...",
  ...
}
```

**O email está no campo `client_email`!**

Exemplo: `pgr-sheets-service@meu-projeto-123456.iam.gserviceaccount.com`

### 4. Colocar o Arquivo no Sistema

1. Crie a pasta `credentials` na raiz do projeto:
   ```bash
   mkdir -p /home/gab/Documentos/PGR/credentials
   ```

2. Renomeie o arquivo JSON baixado para `service_account.json`

3. Mova o arquivo para a pasta:
   ```bash
   mv ~/Downloads/seu-arquivo-baixado.json /home/gab/Documentos/PGR/credentials/service_account.json
   ```

### 5. Verificar se Funciona

Depois de colocar o arquivo, o sistema automaticamente:
- Carrega o email quando você acessa a aba "Google Drive" no upload
- Exibe o email em um box azul no topo da página
- Permite copiar o email com um clique

### 6. Compartilhar Planilha com o Email

1. Abra sua planilha no Google Sheets
2. Clique em **Compartilhar** (canto superior direito)
3. Cole o email do Service Account (o que está em `client_email` no JSON)
4. Defina permissão como **Visualizador**
5. Clique em **Enviar**

## Localização do Arquivo no Sistema

O sistema procura o arquivo em:
- `credentials/service_account.json` (padrão)
- Ou no caminho definido pela variável de ambiente `GOOGLE_CREDENTIALS_PATH`

## Verificar Email via API

Depois de configurar, você pode verificar o email via:

```bash
# Via navegador (precisa estar autenticado)
http://localhost:8001/api/sheets/service-account-email

# Via cURL
curl -X GET "http://localhost:8001/api/sheets/service-account-email" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Resumo Rápido

1. **Criar Service Account** no Google Cloud Console
2. **Baixar JSON** de credenciais
3. **Procurar `client_email`** no JSON (esse é o email!)
4. **Colocar arquivo** em `credentials/service_account.json`
5. **Compartilhar planilha** com esse email
6. **Usar o sistema** - o email aparece automaticamente na interface
