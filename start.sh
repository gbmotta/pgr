#!/bin/bash
set -e

# Garantir que estamos no diretório correto
cd /app || cd /workspace || cd "$(dirname "$0")/.." || pwd

# Instalar dependências Python se necessário
echo "🔍 Verificando dependências Python..."
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "📦 Instalando dependências Python..."
    python3 -m pip install --no-cache-dir -r requirements.txt
fi

# Iniciar servidor
echo "🚀 Iniciando servidor..."
cd backend
exec python3 -m uvicorn api_sqlalchemy:app --host 0.0.0.0 --port ${PORT:-8000}

