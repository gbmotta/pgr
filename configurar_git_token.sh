#!/bin/bash
# Script para configurar Git com token do GitHub

TOKEN=$(cat ~/Documentos/git.txt 2>/dev/null | head -1)

if [ -z "$TOKEN" ]; then
    echo "❌ Token não encontrado em ~/Documentos/git.txt"
    exit 1
fi

echo "🔐 Configurando Git para usar token do GitHub..."
echo ""

# Configurar remote para usar token
cd /home/gab/Documentos/PGR
git remote set-url origin https://${TOKEN}@github.com/gbmotta/pgr.git

echo "✅ Remote configurado com token!"
echo ""
echo "📋 Remote atual:"
git remote -v
echo ""
echo "✅ Agora você pode fazer git push sem senha!"
echo ""
echo "💡 Dica: O token já está configurado no remote. Para outros repositórios,"
echo "   use: git remote set-url origin https://\${TOKEN}@github.com/USUARIO/REPO.git"

