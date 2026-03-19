#!/bin/bash

echo "🔧 Carregando NVM..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "📦 Verificando/Instalando Node.js 18..."
if ! command -v node &> /dev/null 2>&1; then
    echo "Instalando Node.js 18 via NVM..."
    nvm install 18 || {
        echo "❌ Erro ao instalar Node.js 18"
        exit 1
    }
    nvm use 18 || {
        echo "❌ Erro ao usar Node.js 18"
        exit 1
    }
else
    echo "✅ Node.js já instalado: $(node --version)"
fi

echo "🔧 Garantindo que Node.js 18 está ativo..."
nvm use 18 || {
    echo "⚠️  Aviso: não foi possível ativar Node.js 18, usando versão atual"
}

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "📦 Instalando dependências do frontend..."
cd frontend-react || {
    echo "❌ Erro: diretório frontend-react não encontrado"
    exit 1
}

npm install || {
    echo "❌ Erro ao instalar dependências"
    exit 1
}

echo "🏗️  Buildando frontend React..."
npm run build || {
    echo "❌ Erro ao buildar frontend"
    exit 1
}

echo "📋 Verificando build..."
cd "$PROJECT_DIR" || exit 1

# O Vite já builda direto para frontend-dist (configurado no vite.config.js)
if [ -d "frontend-dist" ] && [ -f "frontend-dist/index.html" ]; then
    echo "✅ Frontend buildado com sucesso!"
    echo "📍 Diretório: frontend-dist/"
    ls -la frontend-dist/ | head -5
else
    echo "⚠️  Verificando se precisa copiar de dist..."
    if [ -d "frontend-react/dist" ]; then
        rm -rf frontend-dist
        cp -r frontend-react/dist frontend-dist
        echo "✅ Frontend copiado para frontend-dist/"
    else
        echo "❌ Erro: build não encontrado"
        exit 1
    fi
fi

