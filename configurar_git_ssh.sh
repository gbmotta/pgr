#!/bin/bash
# Script para configurar Git para usar SSH

echo "🔐 Configurando Git para usar SSH..."
echo ""

# Verificar se a chave SSH foi adicionada no GitHub
echo "Testando conexão SSH com GitHub..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ Conexão SSH funcionando!"
    echo ""
    
    # Configurar remote para usar SSH
    echo "Configurando remote do repositório PGR..."
    cd /home/gab/Documentos/PGR
    git remote set-url origin git@github.com:gbmotta/pgr.git
    
    echo "✅ Remote configurado para SSH!"
    echo ""
    echo "📋 Remote atual:"
    git remote -v
    echo ""
    echo "✅ Pronto! Agora você pode fazer git push sem senha!"
else
    echo "❌ SSH ainda não está configurado no GitHub."
    echo ""
    echo "Por favor:"
    echo "1. Copie sua chave SSH:"
    echo ""
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "2. Acesse: https://github.com/settings/keys"
    echo "3. Clique em 'New SSH key'"
    echo "4. Cole a chave acima e salve"
    echo ""
    echo "Depois execute este script novamente."
fi

