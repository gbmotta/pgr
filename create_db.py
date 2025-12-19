#!/usr/bin/env python3
"""
Cria o banco PGR.db a partir de schema.sql, seed.sql e importa processes_initial.csv.
Gera checklist e prazos para cada processo.
"""
import sqlite3
import os
import csv
from datetime import datetime
from db_utils import DB_PATH, get_conn, compute_due_date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')
SEED_PATH = os.path.join(BASE_DIR, 'seed.sql')
CSV_PATH = os.path.join(BASE_DIR, 'processes_initial.csv')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    if os.path.exists(DB_PATH):
        print(f'Removendo banco existente: {DB_PATH}')
        os.remove(DB_PATH)

    conn = get_conn()
    cur = conn.cursor()

    # Criar schema
    print('Aplicando schema...')
    cur.executescript(read_file(SCHEMA_PATH))
    conn.commit()

    # Carregar seeds
    print('Aplicando seeds...')
    cur.executescript(read_file(SEED_PATH))
    conn.commit()

    # Helper: buscar ID
    def get_id(table, col, val):
        cur.execute(f"SELECT id FROM {table} WHERE {col} = ?", (val,))
        row = cur.fetchone()
        return row['id'] if row else None

    # Importar CSV
    print('Importando processos do CSV...')
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            type_id = get_id('process_types', 'code', row['type_code'])
            status_id = get_id('statuses', 'code', row['status_code'])
            if not type_id or not status_id:
                print(f"Aviso: tipo ou status inválido na linha: {row}")
                continue
            
            cur.execute("""
                INSERT OR IGNORE INTO processes
                (protocol_number, type_id, applicant_name, applicant_registration,
                 created_date, status_id, parecer, financial_effective_date, closed_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['protocol_number'],
                type_id,
                row['applicant_name'],
                row['applicant_registration'] or None,
                row['created_date'],
                status_id,
                row['parecer'] or None,
                row['financial_effective_date'] or None,
                row['closed_date'] or None,
                row['notes'] or None
            ))
    conn.commit()
    print('Processos importados.')

    # Gerar checklist de documentos
    print('Gerando checklists de documentos...')
    cur.execute("SELECT id, type_id FROM processes")
    processes = cur.fetchall()
    for proc in processes:
        pid, type_id = proc['id'], proc['type_id']
        cur.execute("""
            SELECT document_id, required, doc_order
            FROM required_documents
            WHERE type_id = ?
            ORDER BY doc_order
        """, (type_id,))
        for doc_row in cur.fetchall():
            cur.execute("""
                INSERT OR IGNORE INTO process_documents
                (process_id, document_id, required, provided)
                VALUES (?, ?, ?, 0)
            """, (pid, doc_row['document_id'], doc_row['required']))
    conn.commit()
    print('Checklists gerados.')

    # Gerar prazos
    print('Gerando prazos...')
    cur.execute("SELECT id, type_id, created_date FROM processes")
    for proc in cur.fetchall():
        pid, type_id, created_date = proc['id'], proc['type_id'], proc['created_date']
        
        cur.execute("""
            SELECT id, days_limit, start_event, is_business_days
            FROM legal_deadlines
            WHERE type_id IS NULL OR type_id = ?
        """, (type_id,))
        
        for ld in cur.fetchall():
            if ld['start_event'] != 'created_date':
                continue
            
            due = compute_due_date(created_date, ld['days_limit'], ld['is_business_days'])
            cur.execute("""
                INSERT OR IGNORE INTO process_deadlines
                (process_id, legal_deadline_id, due_date)
                VALUES (?, ?, ?)
            """, (pid, ld['id'], due))
    
    conn.commit()
    print('Prazos gerados.')
    
    conn.close()
    print(f'Banco criado com sucesso: {DB_PATH}')

if __name__ == '__main__':
    main()
