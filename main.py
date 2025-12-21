"""
Script de entrada para o Railway/Heroku

Este arquivo garante que os imports funcionem corretamente no deploy.
"""
import sys
from pathlib import Path

# Adicionar a raiz do projeto ao PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar a aplicação
from backend.api_sqlalchemy import app

# Expor a variável app para o uvicorn
__all__ = ['app']
