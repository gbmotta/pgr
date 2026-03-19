#!/bin/bash
set -e

echo "🚀 Iniciando Sistema PGR Localmente..."
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}📦 Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.11+ primeiro."
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Execute este script na raiz do projeto (onde está o requirements.txt)"
    exit 1
fi

# Instalar dependências Python se necessário
echo -e "${YELLOW}📦 Verificando dependências Python...${NC}"
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Instalando dependências Python..."
    python3 -m pip install --upgrade pip setuptools wheel
    # Usar --prefer-binary para usar wheels quando disponível (evita necessidade de compilador C)
    python3 -m pip install --prefer-binary -r requirements.txt
else
    echo -e "${GREEN}✅ Dependências Python já instaladas${NC}"
fi

# Instalar dependências Node.js se necessário
echo -e "${YELLOW}📦 Verificando Node.js/npm...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}⚠️  npm não encontrado. O frontend React será pulado.${NC}"
    echo -e "${YELLOW}   Instale Node.js para ter acesso ao frontend completo.${NC}"
    FRONTEND_AVAILABLE=false
else
    echo -e "${GREEN}✅ Node.js/npm encontrado: $(node --version) / $(npm --version)${NC}"
    FRONTEND_AVAILABLE=true
    
    if [ ! -d "frontend-react/node_modules" ]; then
        echo "Instalando dependências Node.js..."
        cd frontend-react
        npm install
        cd ..
    else
        echo -e "${GREEN}✅ Dependências Node.js já instaladas${NC}"
    fi
    
    # Buildar frontend se necessário
    echo -e "${YELLOW}🏗️  Verificando build do frontend...${NC}"
    if [ ! -d "frontend-dist" ] || [ ! -f "frontend-dist/index.html" ]; then
        echo "Buildando frontend React..."
        cd frontend-react
        npm run build
        cd ..
        # Copiar para frontend-dist
        if [ -d "frontend-react/dist" ]; then
            rm -rf frontend-dist
            cp -r frontend-react/dist frontend-dist
            echo -e "${GREEN}✅ Frontend buildado${NC}"
        fi
    else
        echo -e "${GREEN}✅ Frontend já buildado${NC}"
    fi
fi

# Criar diretórios necessários
echo -e "${YELLOW}📁 Criando diretórios...${NC}"
mkdir -p data
mkdir -p uploads
mkdir -p reports
echo -e "${GREEN}✅ Diretórios criados${NC}"

# Inicializar banco de dados se não existir
echo -e "${YELLOW}🗄️  Verificando banco de dados...${NC}"
if [ ! -f "data/PGR.db" ]; then
    echo "Criando banco de dados inicial..."
    python3 -c "
from backend import models_sqlalchemy as models
engine = models.get_engine()
models.create_tables(engine)
print('✅ Tabelas criadas')

# Popular dados iniciais
from backend import seed_sqlalchemy
seed_sqlalchemy.seed_database()
print('✅ Dados iniciais populados')
"
    echo -e "${GREEN}✅ Banco de dados inicializado${NC}"
    echo -e "${YELLOW}👤 Usuário admin criado:${NC}"
    echo -e "   ${GREEN}Usuário: admin${NC}"
    echo -e "   ${GREEN}Senha: admin123${NC}"
else
    echo -e "${GREEN}✅ Banco de dados já existe${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Sistema PGR - Pronto para iniciar!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "📍 Acesse em: ${GREEN}http://localhost:8001${NC}"
echo -e "📚 Documentação API: ${GREEN}http://localhost:8001/docs${NC}"
echo -e "🔍 Health check: ${GREEN}http://localhost:8001/health${NC}"
if [ "$FRONTEND_AVAILABLE" = "false" ]; then
    echo -e "${YELLOW}⚠️  Frontend React não disponível (npm não encontrado)${NC}"
    echo -e "   A API estará funcionando normalmente em /docs${NC}"
fi
echo ""
echo -e "${YELLOW}👤 Credenciais padrão:${NC}"
echo -e "   Usuário: ${GREEN}admin${NC}"
echo -e "   Senha: ${GREEN}admin123${NC}"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para parar o servidor${NC}"
echo ""

# Iniciar servidor
cd backend
python3 -m uvicorn api_sqlalchemy:app --host 0.0.0.0 --port 8001 --reload

