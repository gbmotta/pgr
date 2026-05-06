#!/usr/bin/env bash
# PGR — utilitários de desenvolvimento e build (um único ponto de entrada).
#
# Uso (na raiz do repositório ou de qualquer sítio):
#   ./scripts/pgr.sh help
#   ./scripts/pgr.sh local          # deps, BD inicial, build frontend se faltar, uvicorn --reload
#   ./scripts/pgr.sh build-frontend # npm install/ci + vite build → frontend-dist/
#   ./scripts/pgr.sh serve          # só API + estáticos (PORT do ambiente, default 8001)
#   ./scripts/pgr.sh tunnel [porta] # ngrok → localhost (webhook Google Drive em dev)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cmd="${1:-help}"
shift || true

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

ensure_node() {
  if command -v node &>/dev/null; then
    return 0
  fi
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [[ -s "$NVM_DIR/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    source "$NVM_DIR/nvm.sh"
    nvm install 20 2>/dev/null || nvm install 18 || true
    nvm use 20 2>/dev/null || nvm use 18 2>/dev/null || true
  fi
  command -v node &>/dev/null
}

case "$cmd" in
  help|-h|--help)
    usage
    ;;
  local|dev)
    echo -e "${YELLOW}Iniciando PGR localmente…${NC}"
    if [[ ! -f "$ROOT/requirements.txt" ]]; then
      echo "Execute a partir da raiz do repositório (requirements.txt em falta)."
      exit 1
    fi
    if ! command -v python3 &>/dev/null; then
      echo "Python 3 não encontrado."
      exit 1
    fi
    echo -e "${GREEN}Python $(python3 --version)${NC}"

    if ! python3 -c "import fastapi" &>/dev/null; then
      echo "A instalar dependências Python…"
      python3 -m pip install --upgrade pip setuptools wheel
      python3 -m pip install --prefer-binary -r requirements.txt
    else
      echo -e "${GREEN}Dependências Python OK${NC}"
    fi

    FRONTEND_AVAILABLE=true
    if ! command -v npm &>/dev/null; then
      if ! ensure_node; then
        FRONTEND_AVAILABLE=false
        echo -e "${YELLOW}npm não encontrado — só API (instale Node para o UI integrado em :8001).${NC}"
      fi
    fi

    if [[ "$FRONTEND_AVAILABLE" == true ]]; then
      echo -e "${GREEN}Node $(node --version) / npm $(npm --version)${NC}"
      if [[ ! -d "$ROOT/frontend-react/node_modules" ]]; then
        (cd "$ROOT/frontend-react" && npm install)
      fi
      if [[ ! -f "$ROOT/frontend-dist/index.html" ]]; then
        echo "A compilar frontend (Vite → frontend-dist/)…"
        (cd "$ROOT/frontend-react" && npm run build)
      fi
      if [[ -f "$ROOT/frontend-dist/index.html" ]]; then
        echo -e "${GREEN}frontend-dist pronto${NC}"
      else
        echo -e "${YELLOW}frontend-dist/index.html em falta após o build.${NC}"
      fi
    fi

    mkdir -p data uploads reports

    if [[ ! -f "$ROOT/data/PGR.db" ]]; then
      echo "A criar base e seed…"
      python3 -c "
from backend import models_sqlalchemy as models
engine = models.get_engine()
models.create_tables(engine)
from backend import seed_sqlalchemy
seed_sqlalchemy.seed_database()
print('BD inicial pronta.')
"
      echo -e "${YELLOW}Credenciais por defeito: admin / admin123${NC}"
    else
      echo -e "${GREEN}Base de dados já existe${NC}"
    fi

    echo ""
    echo -e "${GREEN}http://localhost:8001${NC}  ·  API: /docs"
    if [[ "$FRONTEND_AVAILABLE" == false ]]; then
      echo -e "${YELLOW}Sem frontend estático — use npm run dev em frontend-react noutro terminal.${NC}"
    fi
    echo ""
    exec python3 -m uvicorn backend.api_sqlalchemy:app --host 0.0.0.0 --port 8001 --reload
    ;;

  build-frontend)
    if ! command -v npm &>/dev/null; then
      ensure_node || { echo "Node/npm não disponível (instale Node ou NVM)."; exit 1; }
    fi
    cd "$ROOT/frontend-react"
    if [[ -f package-lock.json ]]; then
      npm ci
    else
      npm install
    fi
    npm run build
    if [[ -f "$ROOT/frontend-dist/index.html" ]]; then
      echo -e "${GREEN}Build OK → frontend-dist/${NC}"
    else
      echo "Erro: frontend-dist/index.html não encontrado."
      exit 1
    fi
    ;;

  serve|start)
    PORT="${PORT:-8001}"
    echo "Uvicorn backend.api_sqlalchemy:app em 0.0.0.0:${PORT}"
    exec python3 -m uvicorn backend.api_sqlalchemy:app --host 0.0.0.0 --port "$PORT"
    ;;

  tunnel|webhook-tunnel)
    PORT="${1:-8001}"
    NGROK_BIN=""
    if command -v ngrok >/dev/null 2>&1; then
      NGROK_BIN="$(command -v ngrok)"
    elif [[ -x "${HOME}/bin/ngrok" ]]; then
      NGROK_BIN="${HOME}/bin/ngrok"
    fi
    if [[ -z "${NGROK_BIN}" ]]; then
      echo "ngrok não encontrado. https://ngrok.com/download"
      exit 1
    fi
    echo "Túnel → http://127.0.0.1:${PORT} — copie o https do Forwarding para WEBHOOK_BASE_URL no .env"
    exec "${NGROK_BIN}" http "$PORT"
    ;;

  *)
    echo "Comando desconhecido: $cmd"
    usage
    exit 1
    ;;
esac
