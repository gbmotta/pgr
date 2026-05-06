# PGR — Sistema de processos

Stack: **FastAPI** (`backend/`) + **React/Vite** (`frontend-react/`). Em produção o servidor entrega a API e os ficheiros estáticos em `frontend-dist/` (gerados pelo build do Vite).

## Requisitos locais

- Python 3.11+
- Node.js 20+ (apenas para desenvolvimento / build do frontend)

## Desenvolvimento

```bash
# Raiz: tudo num comando (Python, build do Vite se faltar, SQLite + seed, uvicorn --reload)
./scripts/pgr.sh local
# http://127.0.0.1:8001 — React em modo dev separado: cd frontend-react && npm run dev (:3000)
```

Só compilar o frontend para `frontend-dist/`:

```bash
./scripts/pgr.sh build-frontend
```

Servidor sem reload (útil para testar como em produção):

```bash
PORT=8001 ./scripts/pgr.sh serve
```

Equivalente ao arranque mínimo: `python start_app.py` (usa `PORT` do ambiente, default 8001).

Variáveis: copie `.env.example` para `.env` na raiz e ajuste.

## Produção (recomendado: Docker)

```bash
docker build -t pgr-app .
docker run -p 8001:8001 \
  -e PORT=8001 \
  --env-file .env \
  -v pgr-data:/app/data \
  -v pgr-uploads:/app/uploads \
  pgr-app
```

- Monte volumes em `data/` (SQLite), `uploads/` e, se usar, pasta de credenciais Google.
- Defina `PORT` se a plataforma o injeta (ex.: 8080).
- Para **PostgreSQL** ou outro BD, altere `DATABASE_URL` / configuração em `backend/models_sqlalchemy.py` conforme o vosso ambiente (hoje o padrão é SQLite em `data/`).

## Produção sem Docker (VPS)

1. Clonar o repositório, Python 3.11, `pip install -r requirements.txt`.
2. `cd frontend-react && npm ci && npm run build`.
3. Servir com **gunicorn + uvicorn workers** ou `uvicorn` atrás de **Nginx** (TLS, limite de corpo, cache de estáticos):

```bash
export PORT=8001
python start_app.py
```

4. Colocar Nginx como reverse proxy para `127.0.0.1:8001`, domínio e certificado (Let’s Encrypt).
5. Processo persistente: **systemd**, **supervisor** ou **Docker**.

## Clientes (checklist)

- Ficheiro `.env` com segredos reais (não commitar).
- Primeiro utilizador registado como admin (ver lógica em `api_sqlalchemy`) ou credenciais definidas no vosso fluxo.
- Conta de **Google** (service account) se usarem Drive/Sheets: JSON de credenciais no servidor e URLs/webhook conforme `webhook_config.py`.
- Backups de `data/*.db` (ou dump do Postgres) e de `uploads/`.
- CORS: em `api_sqlalchemy.py` restrinja `allow_origins` ao domínio do cliente em produção.

## Scripts

- `./scripts/pgr.sh` — `local` | `build-frontend` | `serve` | `tunnel [porta]` | `help`. O túnel (`tunnel`) expõe o backend para testar o webhook do Google Drive em desenvolvimento.
