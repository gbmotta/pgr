#!/usr/bin/env python3
"""
CLI para marcar documento como fornecido.
Uso: python3 attach_document.py <protocol> <document_code> [provided_date]
Exemplo: python3 attach_document.py PGR-2025-0001 CERT_CURSO 2025-12-15
"""
import sys
from db_utils import get_conn
from datetime import date

def main():
    if len(sys.argv) < 3:
        print("Uso: attach_document.py <protocol> <document_code> [provided_date YYYY-MM-DD]")
        sys.exit(1)
    
    protocol = sys.argv[1]
    doc_code = sys.argv[2]
    provided_date = sys.argv[3] if len(sys.argv) >= 4 else date.today().isoformat()
    
    conn = get_conn()
    cur = conn.cursor()
    
    # Buscar processo
    cur.execute("SELECT id FROM processes WHERE protocol_number = ?", (protocol,))
    proc = cur.fetchone()
    if not proc:
        print(f"Erro: Processo {protocol} não encontrado")
        conn.close()
        sys.exit(2)
    
    # Buscar documento
    cur.execute("SELECT id FROM documents WHERE code = ?", (doc_code,))
    doc = cur.fetchone()
    if not doc:
        print(f"Erro: Documento {doc_code} não encontrado")
        conn.close()
        sys.exit(3)
    
    # Atualizar
    cur.execute("""
        UPDATE process_documents
        SET provided = 1, provided_date = ?
        WHERE process_id = ? AND document_id = ?
    """, (provided_date, proc['id'], doc['id']))
    
    if cur.rowcount == 0:
        print(f"Erro: Item de checklist não encontrado")
        conn.close()
        sys.exit(4)
    
    conn.commit()
    print(f"✓ Documento {doc_code} marcado como fornecido em {provided_date}")
    conn.close()

if __name__ == '__main__':
    main()
