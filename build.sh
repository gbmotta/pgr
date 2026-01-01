#!/bin/bash
# Script de build para Railway
set -e

echo "🔨 Iniciando build..."

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependências Python instaladas!"

# Build do frontend React
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
        echo "Conteúdo:"
        ls -la frontend-dist/ | head -10
        if [ -f "frontend-dist/index.html" ]; then
            echo "✅ index.html encontrado!"
        else
            echo "❌ ERRO: index.html não encontrado em frontend-dist/"
            exit 1
        fi
    else
        echo "❌ ERRO: frontend-dist/ não foi criado!"
        echo "Verificando se foi criado em outro local..."
        find . -name "frontend-dist" -type d 2>/dev/null || echo "Não encontrado"
        exit 1
    fi
else
    echo "⚠️  Pasta frontend-react não encontrada"
    exit 1
fi

echo "✅ Build concluído com sucesso!"

