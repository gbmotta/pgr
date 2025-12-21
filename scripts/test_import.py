#!/usr/bin/env python3
"""Testa importação do Excel com debug detalhado"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd

# Ler o arquivo Excel
excel_file = 'tests_data/processos_dashboard_completo.xlsx'
print(f"📂 Lendo: {excel_file}")

try:
    df = pd.read_excel(excel_file)
    print(f"✅ {len(df)} linhas encontradas")
    print(f"\n📋 Colunas: {list(df.columns)}")
    print(f"\n🔍 Primeiras 3 linhas:")
    print(df.head(3))
    
    print(f"\n🔍 Tipos de dados:")
    print(df.dtypes)
    
    print(f"\n🔍 Valores únicos de Status:")
    if 'Status' in df.columns:
        print(df['Status'].unique())
    
    print(f"\n🔍 Valores nulos por coluna:")
    print(df.isnull().sum())
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
