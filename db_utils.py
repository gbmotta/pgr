"""
Funções utilitárias para interação com banco de dados SQLite.
"""
import sqlite3
from datetime import datetime, timedelta, date
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'PGR.db')

def get_conn():
    """Retorna conexão SQLite com foreign keys habilitado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def add_business_days(start_date: date, days: int) -> date:
    """Adiciona dias úteis (segunda a sexta) a uma data."""
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # 0=Mon, 4=Fri
            added += 1
    return current

def compute_due_date(start_iso: str, days_limit: int, is_business: bool) -> str:
    """Calcula data de vencimento a partir de start_iso (YYYY-MM-DD)."""
    start = datetime.strptime(start_iso, '%Y-%m-%d').date()
    if is_business:
        due = add_business_days(start, days_limit)
    else:
        due = start + timedelta(days=days_limit)
    return due.isoformat()
