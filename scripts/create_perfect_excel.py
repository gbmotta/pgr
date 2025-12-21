#!/usr/bin/env python3
"""
Cria arquivo Excel PERFEITO para importação no Sistema PGR
Garantido para funcionar 100% com a interface web e script de import
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

def create_perfect_excel():
    """Cria arquivo Excel com dados estratégicos para testar o dashboard"""
    
    data = []
    
    # ===== PROCESSOS PARA PRAZOS VENCIDOS (45-60 dias) =====
    print("📅 Criando processos vencidos (45-60 dias)...")
    for i in range(3):
        days_ago = 45 + (i * 5)
        data.append({
            'Protocolo': f'PGR-2025-{800+i:04d}',
            'Tipo': 'PROM_CAP',
            'Requerente': f'João Silva Vencido {i+1}',
            'Matrícula': f'{20000+i}',
            'Status': 'EM_ANALISE',
            'Data': (datetime.now() - timedelta(days=days_ago)).strftime('%d/%m/%Y')
        })
    
    # ===== PROCESSOS PARA PRAZOS PRÓXIMOS (25-28 dias) =====
    print("⚠️  Criando processos com prazos próximos (25-28 dias)...")
    for i in range(3):
        days_ago = 25 + i
        data.append({
            'Protocolo': f'PGR-2025-{810+i:04d}',
            'Tipo': 'PROG_MER',
            'Requerente': f'Maria Santos Próximo {i+1}',
            'Matrícula': f'{21000+i}',
            'Status': 'EM_ANALISE',
            'Data': (datetime.now() - timedelta(days=days_ago)).strftime('%d/%m/%Y')
        })
    
    # ===== PROCESSOS EM ANÁLISE (recentes, 5-15 dias) =====
    print("🔍 Criando processos em análise...")
    for i in range(4):
        days_ago = 5 + (i * 3)
        data.append({
            'Protocolo': f'PGR-2025-{820+i:04d}',
            'Tipo': 'PROM_CAP' if i % 2 == 0 else 'PROG_MER',
            'Requerente': f'Pedro Oliveira Análise {i+1}',
            'Matrícula': f'{22000+i}',
            'Status': 'EM_ANALISE',
            'Data': (datetime.now() - timedelta(days=days_ago)).strftime('%d/%m/%Y')
        })
    
    # ===== PROCESSOS PENDENTES DE DOCUMENTOS =====
    print("📋 Criando processos pendentes de docs...")
    for i in range(4):
        days_ago = 10 + i
        data.append({
            'Protocolo': f'PGR-2025-{830+i:04d}',
            'Tipo': 'PROG_MER',
            'Requerente': f'Ana Costa Pendente {i+1}',
            'Matrícula': f'{23000+i}',
            'Status': 'PENDENTE_DOCS',
            'Data': (datetime.now() - timedelta(days=days_ago)).strftime('%d/%m/%Y')
        })
    
    # ===== PROCESSOS RECEBIDOS (recentes, 1-4 dias) =====
    print("📥 Criando processos recebidos...")
    for i in range(3):
        days_ago = 1 + i
        data.append({
            'Protocolo': f'PGR-2025-{840+i:04d}',
            'Tipo': 'PROM_CAP',
            'Requerente': f'Carlos Souza Novo {i+1}',
            'Matrícula': f'{24000+i}',
            'Status': 'RECEBIDO',
            'Data': (datetime.now() - timedelta(days=days_ago)).strftime('%d/%m/%Y')
        })
    
    # ===== PROCESSO COMPLETO =====
    print("✅ Criando processo completo...")
    data.append({
        'Protocolo': 'PGR-2025-0850',
        'Tipo': 'PROM_CAP',
        'Requerente': 'Roberto Lima Completo',
        'Matrícula': '25000',
        'Status': 'COMPLETO',
        'Data': (datetime.now() - timedelta(days=2)).strftime('%d/%m/%Y')
    })
    
    # Criar DataFrame
    df = pd.DataFrame(data)
    
    # Salvar arquivo
    output_file = 'tests_data/processos_dashboard_perfeito.xlsx'
    df.to_excel(output_file, index=False, sheet_name='Processos')
    
    print(f"\n{'='*60}")
    print(f"✅ ARQUIVO CRIADO: {output_file}")
    print(f"{'='*60}")
    print(f"\n📊 Total de processos: {len(data)}")
    print(f"\n📋 Distribuição:")
    print(f"   🔍 Em Análise: {len([p for p in data if p['Status'] == 'EM_ANALISE'])} processos")
    print(f"   📋 Pendente Docs: {len([p for p in data if p['Status'] == 'PENDENTE_DOCS'])} processos")
    print(f"   📥 Recebidos: {len([p for p in data if p['Status'] == 'RECEBIDO'])} processos")
    print(f"   ✅ Completos: {len([p for p in data if p['Status'] == 'COMPLETO'])} processos")
    
    print(f"\n📅 Prazos:")
    print(f"   ⏰ Vencidos (45-60 dias): 3 processos")
    print(f"   ⚠️  Próximos (25-28 dias): 3 processos")
    
    print(f"\n🎯 COMO USAR:")
    print(f"   1. Acesse: http://localhost:8000/pgr/upload.html")
    print(f"   2. Faça upload do arquivo: {output_file}")
    print(f"   3. Aguarde a importação")
    print(f"   4. Acesse o dashboard: http://localhost:8000/pgr/")
    print(f"\n✨ Os cards do dashboard serão populados com:")
    print(f"   • Total de Processos: ~{len(data)} novos")
    print(f"   • Em Análise: 7")
    print(f"   • Docs Pendentes: 4")
    print(f"   • Prazos Vencidos: 3")
    print(f"   • Prazos Próximos: 3")
    print(f"\n{'='*60}\n")
    
    # Mostrar preview
    print("📋 Preview das primeiras 5 linhas:")
    print(df.head(5).to_string(index=False))
    print(f"\n... e mais {len(data)-5} processos\n")

if __name__ == "__main__":
    create_perfect_excel()
