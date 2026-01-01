#!/bin/bash
# Script de build para Railway
set -e

echo "🔨 Iniciando build..."

# Instalar dependências Python (Nixpacks faz isso automaticamente, mas garantimos)
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependências Python..."
    pip install -r requirements.txt
fi

# Build do frontend React
if [ -d "frontend-react" ]; then
    echo "📦 Instalando dependências Node.js..."
    cd frontend-react
    npm install
    echo "🏗️  Fazendo build do React..."
    npm run build
    cd ..
    echo "✅ Frontend buildado em frontend-dist/"
else
    echo "⚠️  Pasta frontend-react não encontrada"
fi

echo "✅ Build concluído!"

