#!/usr/bin/env python3
"""
Script de inicialização robusta para o servidor FastAPI
Verifica dependências e inicializa o servidor com tratamento de erros
"""
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Verificar imports básicos
print("🔍 Verificando dependências...")
try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI não encontrado: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"✅ Uvicorn {uvicorn.__version__}")
except ImportError as e:
    print(f"❌ Uvicorn não encontrado: {e}")
    sys.exit(1)

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy não encontrado: {e}")
    sys.exit(1)

# Verificar se backend pode ser importado
print("🔍 Verificando módulos do backend...")
try:
    from backend import api_sqlalchemy
    print("✅ backend.api_sqlalchemy importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar backend.api_sqlalchemy: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verificar app
if not hasattr(api_sqlalchemy, 'app'):
    print("❌ app não encontrado em api_sqlalchemy")
    sys.exit(1)

print("✅ App FastAPI encontrado")

# Porta - Railway fornece via variável de ambiente
port = int(os.environ.get('PORT', 8001))
host = '0.0.0.0'  # Railway precisa escutar em 0.0.0.0

print(f"🚀 Iniciando servidor em {host}:{port}...")
print(f"📂 Diretório de trabalho: {os.getcwd()}")
print(f"🐍 Python: {sys.executable}")

# Iniciar servidor
try:
    print("=" * 50)
    print(f"🚀 SERVIDOR INICIANDO")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   App: backend.api_sqlalchemy:app")
    print("=" * 50)
    uvicorn.run(
        "backend.api_sqlalchemy:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

