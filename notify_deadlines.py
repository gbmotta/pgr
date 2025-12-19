#!/usr/bin/env python3
"""
Lista prazos vencidos e marca como notificado.
Uso:
  python3 notify_deadlines.py           # apenas lista
  python3 notify_deadlines.py --mark    # lista e marca notificados
"""
import argparse
from db_utils import get_conn
from datetime import date

def main():
    parser = argparse.ArgumentParser(description='Gerenciar notificações de prazos vencidos')
    parser.add_argument('--mark', action='store_true', help='Marcar prazos como notificados')
    args = parser.parse_args()
    
    conn = get_conn()
    cur = conn.cursor()
    today = date.today().isoformat()
    
    cur.execute("""
        SELECT pdl.id, p.protocol_number, ld.name AS deadline_name,
               pdl.due_date, julianday(?) - julianday(pdl.due_date) AS days_overdue,
               pdl.notified
        FROM process_deadlines pdl
        JOIN processes p ON p.id = pdl.process_id
        JOIN legal_deadlines ld ON ld.id = pdl.legal_deadline_id
        WHERE pdl.closed = 0 AND pdl.due_date < ?
        ORDER BY pdl.due_date ASC
    """, (today, today))
    
    rows = cur.fetchall()
    
    if not rows:
        print("Nenhum prazo vencido encontrado.")
        conn.close()
        return
    
    print(f"\n{'='*80}")
    print(f"PRAZOS VENCIDOS ({len(rows)} encontrado(s))")
    print(f"{'='*80}\n")
    
    ids_to_mark = []
    for r in rows:
        days = int(round(r['days_overdue']))
        notified = "✓" if r['notified'] else "✗"
        print(f"[ID {r['id']:3d}] {r['protocol_number']:15s} | {r['deadline_name']:30s}")
        print(f"         Vencimento: {r['due_date']} ({days} dias atrás) | Notificado: {notified}\n")
        if not r['notified']:
            ids_to_mark.append(r['id'])
    
    if args.mark and ids_to_mark:
        placeholders = ','.join('?' * len(ids_to_mark))
        cur.execute(f"UPDATE process_deadlines SET notified = 1 WHERE id IN ({placeholders})", ids_to_mark)
        conn.commit()
        print(f"✓ {len(ids_to_mark)} prazo(s) marcado(s) como notificado(s)")
    
    conn.close()

if __name__ == '__main__':
    main()
