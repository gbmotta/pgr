"""
Backend do Sistema PGR - Processos Administrativos

Este pacote contém toda a lógica de backend do sistema:
- api_sqlalchemy.py: API REST com FastAPI
- models_sqlalchemy.py: Modelos do banco de dados (ORM)
- seed_sqlalchemy.py: Script para popular dados iniciais

Para rodar o servidor:
    uvicorn backend.api_sqlalchemy:app --reload

Para deploy (Railway/Heroku):
    uvicorn backend.api_sqlalchemy:app --host 0.0.0.0 --port $PORT
"""

__version__ = "2.0.0"
__author__ = "Sistema PGR"
