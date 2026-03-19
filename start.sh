#!/bin/bash
set -e

# Encontrar diretório raiz do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "📂 Diretório atual: $(pwd)"
echo "📦 Verificando Python..."
which python3 || which python || (echo "Python não encontrado!" && exit 1)

echo "🚀 Iniciando servidor FastAPI..."
cd backend || (echo "Diretório backend não encontrado!" && exit 1)

echo "📂 Diretório backend: $(pwd)"
echo "🐍 Python: $(which python3)"
echo "📋 PORT: ${PORT:-8001}"

exec python3 -m uvicorn api_sqlalchemy:app --host 0.0.0.0 --port ${PORT:-8001}

