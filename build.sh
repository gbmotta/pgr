#!/bin/bash
# Script de build para Railway
# Nota: Nixpacks já instala dependências Python automaticamente via requirements.txt
set -e

echo "🔨 Iniciando build do frontend React..."

# Build do frontend React
if [ -d "frontend-react" ]; then
    echo "📦 Instalando dependências Node.js..."
    cd frontend-react
    npm install
    echo "🏗️  Fazendo build do React..."
    npm run build
    cd ..
    echo "✅ Frontend buildado em frontend-dist/"
    
    # Verificar se o build foi criado
    if [ -d "frontend-dist" ]; then
        echo "✅ frontend-dist/ criado com sucesso!"
        ls -la frontend-dist/ | head -5
    else
        echo "❌ ERRO: frontend-dist/ não foi criado!"
        exit 1
    fi
else
    echo "⚠️  Pasta frontend-react não encontrada"
    exit 1
fi

echo "✅ Build concluído com sucesso!"

