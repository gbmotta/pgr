#!/bin/bash
# Script para expor a API localmente via túnel (demonstração/teste)

echo "🌐 Exposição da API PGR via Túnel"
echo "=================================="
echo ""

# Verificar se a API está rodando
if ! lsof -i:8000 > /dev/null 2>&1; then
    echo "⚠️  API não está rodando na porta 8000"
    echo ""
    echo "Iniciando API..."
    source ~/miniconda3/bin/activate pgr-env
    cd /home/gab/Documentos/PGR
    uvicorn api_sqlalchemy:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    API_PID=$!
    echo "✓ API iniciada (PID: $API_PID)"
    sleep 3
fi

echo ""
echo "Escolha a ferramenta de túnel:"
echo "1) ngrok (requer instalação: sudo snap install ngrok)"
echo "2) localtunnel (requer: npm install -g localtunnel)"
echo "3) Cloudflare Tunnel (requer cloudflared)"
echo ""
read -p "Opção [1-3]: " opcao

case $opcao in
    1)
        echo ""
        echo "Iniciando ngrok..."
        if command -v ngrok &> /dev/null; then
            ngrok http 8000
        else
            echo "❌ ngrok não instalado. Instale com:"
            echo "   sudo snap install ngrok"
        fi
        ;;
    2)
        echo ""
        echo "Iniciando localtunnel..."
        if command -v lt &> /dev/null; then
            lt --port 8000
        else
            echo "❌ localtunnel não instalado. Instale com:"
            echo "   npm install -g localtunnel"
        fi
        ;;
    3)
        echo ""
        echo "Iniciando Cloudflare Tunnel..."
        if command -v cloudflared &> /dev/null; then
            cloudflared tunnel --url http://localhost:8000
        else
            echo "❌ cloudflared não instalado. Baixe em:"
            echo "   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        fi
        ;;
    *)
        echo "Opção inválida"
        exit 1
        ;;
esac
