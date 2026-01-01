#!/bin/bash
set -e

# Garantir que estamos no diretório correto
cd "$(dirname "$0")" || cd /app || cd /workspace || pwd

# Nixpacks já instalou dependências no build
# Apenas iniciar servidor
echo "🚀 Iniciando servidor..."
cd backend
exec python3 -m uvicorn api_sqlalchemy:app --host 0.0.0.0 --port ${PORT:-8000}

