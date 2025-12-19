#!/bin/bash
# Script de instalação e execução rápida do sistema

echo "🚀 Sistema de Processos Administrativos - Instalação"
echo "===================================================="
echo ""

# 1. Verificar Python
echo "1. Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8 ou superior."
    exit 1
fi
echo "✓ Python3 encontrado: $(python3 --version)"
echo ""

# 2. Instalar dependências
echo "2. Instalando dependências..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências."
    exit 1
fi
echo "✓ Dependências instaladas"
echo ""

# 3. Popular banco de dados
echo "3. Populando banco de dados..."
python3 seed_sqlalchemy.py
if [ $? -ne 0 ]; then
    echo "❌ Erro ao popular banco."
    exit 1
fi
echo "✓ Banco de dados populado"
echo ""

# 4. Testar sistema
echo "4. Testando sistema..."
python3 test_system.py
echo ""

# 5. Instruções finais
echo "===================================================="
echo "✅ Instalação concluída!"
echo ""
echo "Para executar a API:"
echo "  python3 api_sqlalchemy.py"
echo ""
echo "Ou:"
echo "  uvicorn api_sqlalchemy:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Documentação: http://localhost:8000/docs"
echo "===================================================="
