#!/usr/bin/env python3
"""
Atualiza os status dos processos de teste para popular o dashboard
"""

from backend.models_sqlalchemy import get_session, Process
from datetime import datetime, timedelta

def update_test_processes():
    from backend.models_sqlalchemy import get_engine
    session = get_session(get_engine())
    
    # Processos para prazos vencidos (45-60 dias atrás)
    vencidos = ['PGR-2025-0500', 'PGR-2025-0501', 'PGR-2025-0502']
    for protocol in vencidos:
        p = session.query(Process).filter_by(protocol_number=protocol).first()
        if p:
            p.status_code = 'EM_ANALISE'
            days_ago = 45 + vencidos.index(protocol) * 5
            p.created_date = (datetime.now() - timedelta(days=days_ago)).date()
            print(f"✅ {protocol}: EM_ANALISE, {days_ago} dias atrás")
    
    # Processos para prazos próximos (25-28 dias atrás)
    proximos = ['PGR-2025-0503', 'PGR-2025-0504', 'PGR-2025-0505']
    for protocol in proximos:
        p = session.query(Process).filter_by(protocol_number=protocol).first()
        if p:
            p.status_code = 'EM_ANALISE'
            days_ago = 25 + proximos.index(protocol)
            p.created_date = (datetime.now() - timedelta(days=days_ago)).date()
            print(f"✅ {protocol}: EM_ANALISE, {days_ago} dias atrás")
    
    # Processos em análise (recentes)
    em_analise = ['PGR-2025-0506', 'PGR-2025-0507', 'PGR-2025-0508', 'PGR-2025-0509']
    for protocol in em_analise:
        p = session.query(Process).filter_by(protocol_number=protocol).first()
        if p:
            p.status_code = 'EM_ANALISE'
            p.created_date = (datetime.now() - timedelta(days=10)).date()
            print(f"✅ {protocol}: EM_ANALISE, 10 dias atrás")
    
    # Processos pendente de documentos
    pendentes = ['PGR-2025-0510', 'PGR-2025-0511', 'PGR-2025-0512', 'PGR-2025-0513']
    for protocol in pendentes:
        p = session.query(Process).filter_by(protocol_number=protocol).first()
        if p:
            p.status_code = 'PENDENTE_DOCS'
            p.created_date = (datetime.now() - timedelta(days=5)).date()
            print(f"✅ {protocol}: PENDENTE_DOCS, 5 dias atrás")
    
    # Processo completo
    p = session.query(Process).filter_by(protocol_number='PGR-2025-0514').first()
    if p:
        p.status_code = 'COMPLETO'
        p.created_date = (datetime.now() - timedelta(days=2)).date()
        print(f"✅ PGR-2025-0514: COMPLETO, 2 dias atrás")
    
    session.commit()
    print("\n✅ Status atualizados com sucesso!")
    session.close()

if __name__ == '__main__':
    update_test_processes()
