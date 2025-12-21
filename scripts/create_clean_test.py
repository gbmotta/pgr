#!/usr/bin/env python3
"""Cria arquivo Excel de teste GARANTIDO para funcionar"""

import pandas as pd
from datetime import datetime, timedelta

# Dados limpos e testados
data = []

# 3 processos vencidos (45-60 dias)
for i in range(3):
    data.append({
        'Protocolo': f'PGR-2025-0600',
        'Tipo': 'PROM_CAP',
        'Requerente': f'Servidor Teste {i+1}',
        'Matrícula': f'MAT{1000+i}',
        'Status': 'EM_ANALISE',
        'Data': (datetime.now() - timedelta(days=45+i*5)).strftime('%d/%m/%Y'),
        'Efeito Financeiro': (datetime.now() - timedelta(days=30+i*5)).strftime('%d/%m/%Y'),
        'Parecer': 'Em análise técnica'
    })

# 3 processos próximos (25-28 dias)
for i in range(3):
    data.append({
        'Protocolo': f'PGR-2025-{610+i}',
        'Tipo': 'PROG_MER',
        'Requerente': f'Servidor Análise {i+1}',
        'Matrícula': f'MAT{2000+i}',
        'Status': 'EM_ANALISE',
        'Data': (datetime.now() - timedelta(days=25+i)).strftime('%d/%m/%Y'),
        'Efeito Financeiro': '',
        'Parecer': 'Aguardando revisão'
    })

# 4 processos pendentes
for i in range(4):
    data.append({
        'Protocolo': f'PGR-2025-{620+i}',
        'Tipo': 'PROM_CAP',
        'Requerente': f'Servidor Pendente {i+1}',
        'Matrícula': f'MAT{3000+i}',
        'Status': 'PENDENTE_DOCS',
        'Data': (datetime.now() - timedelta(days=10)).strftime('%d/%m/%Y'),
        'Efeito Financeiro': '',
        'Parecer': 'Documentação incompleta'
    })

# 3 processos recentes
for i in range(3):
    data.append({
        'Protocolo': f'PGR-2025-{630+i}',
        'Tipo': 'PROG_MER',
        'Requerente': f'Servidor Novo {i+1}',
        'Matrícula': f'MAT{4000+i}',
        'Status': 'RECEBIDO',
        'Data': (datetime.now() - timedelta(days=2+i)).strftime('%d/%m/%Y'),
        'Efeito Financeiro': '',
        'Parecer': ''
    })

df = pd.DataFrame(data)
output_file = 'tests_data/processos_teste_limpo.xlsx'
df.to_excel(output_file, index=False, sheet_name='Processos')

print(f"✅ Arquivo criado: {output_file}")
print(f"📊 {len(df)} processos")
print(f"\n📋 Colunas: {list(df.columns)}")
print(f"\n🔍 Status:")
print(df['Status'].value_counts())
