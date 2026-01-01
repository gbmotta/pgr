#!/bin/bash
# Script para setup inicial no Railway

echo "🚀 Setup inicial do Sistema PGR no Railway"
echo "=========================================="
echo ""

# Instalar Railway CLI (se não tiver)
if ! command -v railway &> /dev/null; then
    echo "📦 Instalando Railway CLI..."
    npm install -g @railway/cli
fi

echo "🔐 Fazendo login no Railway..."
railway login

echo "🔗 Vinculando ao projeto..."
railway link

echo "🌱 Executando seed do banco de dados..."
railway run python backend/seed_sqlalchemy.py

echo ""
echo "✅ Setup concluído!"
echo ""
echo "📝 Credenciais padrão:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  IMPORTANTE: Altere a senha em produção!"

