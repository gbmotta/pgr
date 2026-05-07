# PGR

Sistema de gestão de processos com backend em **FastAPI** (`backend/`) e frontend em **React + Vite** (`frontend-react/`). Em produção, a aplicação serve a API e os ficheiros estáticos gerados em `frontend-dist/`.

## Stack

- Python 3.11+
- FastAPI
- React + Vite
- SQLite por padrão
- Docker / Docker Compose para produção recomendada

## Estrutura

- `backend/`: API, autenticação, integração com Google, regras de negócio
- `frontend-react/`: interface web
- `deploy/`: `compose.yml` e `Caddyfile` para produção
- `scripts/`: utilitários de arranque e bootstrap
- `start_app.py`: arranque simples da aplicação

## Desenvolvimento local

Requisitos:

- Python 3.11+
- Node.js 20+

Arranque rápido:

```bash
./scripts/pgr.sh local
```

Isto sobe o backend localmente e trata do frontend quando necessário.

URLs:

- App/API: `http://127.0.0.1:8001`
- Frontend Vite em dev separado: `cd frontend-react && npm run dev`

Build manual do frontend:

```bash
./scripts/pgr.sh build-frontend
```

Executar sem reload:

```bash
PORT=8001 ./scripts/pgr.sh serve
```

Equivalente mínimo:

```bash
python start_app.py
```

## Variáveis de ambiente

Copie o ficheiro de exemplo para `.env` na raiz e ajuste os valores do seu ambiente.

Em produção, as variáveis mais importantes são:

- `PORT`: porta do servidor
- `APP_DOMAIN`: domínio público da aplicação
- `WEBHOOK_BASE_URL`: URL base HTTPS usada em integrações/webhooks
- `SECRET_KEY`: segredo principal da aplicação
- `GOOGLE_WEBHOOK_SECRET`: segredo para validação do webhook Google

## Produção recomendada

Para este projeto, a opção mais equilibrada é:

- **VPS**
- **Docker Compose**
- **Caddy**
- **domínio próprio**

Arquivos já preparados:

- `deploy/compose.yml`
- `deploy/Caddyfile`
- `.env.production.example`
- `scripts/bootstrap_vps.sh`

## Deploy rápido na VPS

### 1. Domínio

Pode usar:

- Cloudflare Registrar
- Registro.br
- Namecheap

Crie o domínio e guarde acesso ao painel DNS.

### 2. VPS

Recomendado:

- Hetzner Cloud

Alternativas:

- DigitalOcean
- Vultr

Configuração inicial sugerida:

- Ubuntu 22.04 LTS
- 2 vCPU
- 4 GB RAM
- SSD suficiente para uploads e base de dados

Garanta que as portas `80` e `443` estão liberadas.

### 3. DNS

Crie um registo `A` apontando o domínio ou subdomínio para o IP público da VPS.

Exemplo:

- `app.seudominio.com` -> `IP_DA_VPS`

Teste:

```bash
dig +short app.seudominio.com
```

### 4. Clonar o projeto

```bash
git clone <repo>
cd PGR
```

### 5. Configurar `.env`

```bash
cp .env.production.example .env
```

Preencha pelo menos:

- `APP_DOMAIN`
- `WEBHOOK_BASE_URL`
- `SECRET_KEY`
- `GOOGLE_WEBHOOK_SECRET`

### 6. Subir com Docker Compose

```bash
cd deploy
docker compose up -d --build
```

### 7. Verificar

```bash
cd deploy
docker compose ps
docker compose logs -f
```

Depois aceda a:

- `https://app.seudominio.com`
- `https://app.seudominio.com/docs`

## Deploy automático com bootstrap

Se quiser automatizar a preparação da VPS:

```bash
bash /opt/PGR/scripts/bootstrap_vps.sh \
  --repo https://github.com/SEU_USUARIO/PGR.git \
  --domain app.seudominio.com \
  --secret-key "GERE_UMA_CHAVE_LONGA_E_ALEATORIA" \
  --webhook-secret "GERE_OUTRO_SEGREDO_FORTE"
```

O script:

- instala Docker e Compose
- ajusta firewall
- clona ou atualiza o projeto
- cria `.env`
- sobe os containers

## Produção sem Docker

Se não quiser Docker:

1. Instale Python 3.11 e dependências
2. Faça o build do frontend
3. Sirva a aplicação com `uvicorn` ou `gunicorn`
4. Coloque Nginx na frente para HTTPS e proxy reverso
5. Use `systemd`, `supervisor` ou equivalente para manter o processo ativo

Comandos base:

```bash
pip install -r requirements.txt
cd frontend-react && npm ci && npm run build
export PORT=8001
python start_app.py
```

## Google Drive / Google Sheets

Se usar integração com Google:

1. Crie um projeto no Google Cloud Console
2. Ative as APIs necessárias
3. Crie uma service account
4. Gere o JSON de credenciais
5. Coloque o ficheiro no servidor com permissões restritas
6. Partilhe as planilhas com o email da service account como leitor

As referências de integração estão no código em `backend/webhook_config.py` e serviços relacionados.

## Persistência e backups

Em Docker, os volumes principais são:

- `pgr_data`
- `pgr_uploads`
- `pgr_reports`

Recomendação mínima:

- backup diário
- cópia fora da VPS
- teste de restauração periodicamente

## Atualização de versão

Na VPS:

```bash
cd /opt/PGR
git pull
cd deploy
docker compose up -d --build
```

## Operação e checklist

Antes de entregar para clientes:

- configurar `.env` com segredos reais
- validar domínio e HTTPS
- testar login
- testar importação de planilha
- testar relatórios
- testar calendário
- testar integração Google, se aplicável
- configurar backups
- restringir CORS em produção

## Scripts úteis

- `./scripts/pgr.sh local`
- `./scripts/pgr.sh build-frontend`
- `./scripts/pgr.sh serve`
- `./scripts/pgr.sh tunnel [porta]`
- `./scripts/pgr.sh help`

## Notas

- O primeiro utilizador pode assumir papel administrativo conforme a lógica atual da aplicação.
- O padrão atual de base de dados é SQLite em `data/`.
- Se migrar para PostgreSQL ou outro banco, ajuste a configuração no backend conforme o ambiente.
