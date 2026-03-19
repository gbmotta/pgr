#!/usr/bin/env python3
"""
Script para testar upload de planilha XLSX.
Cria um arquivo de exemplo e testa o upload via API.
"""
import os
import sys
import requests
import pandas as pd
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = os.getenv('API_URL', 'http://localhost:8001')

def create_example_file():
    """Cria arquivo XLSX de exemplo."""
    data = {
        'PROCESSO ADM 1DOC': [
            'PGR-2025-001',
            'PGR-2025-002',
            None
        ],
        'PROCESSO JUDICIAL': [
            None,
            None,
            '1234567-89.2025.8.26.0001'
        ],
        'PARTES': [
            'João Silva, Maria Santos',
            'Pedro Oliveira',
            'Ana Costa'
        ],
        'DATA RECEBIMENTO (MÊS/ANO)': [
            'DEZ/2025',
            'NOV/2025',
            'OUT/2025'
        ],
        'TEMA – OBSERVAÇÕES': [
            'Processo de promoção por capacitação profissional. Requerente possui certificados válidos.',
            'Progressão por mérito profissional. Análise de desempenho em andamento.',
            'Processo administrativo relacionado a progressão funcional.'
        ],
        'PRAZO INFO – ESTAG (DIA/MÊS)': [
            '13/02',
            '15/03',
            '10/04'
        ],
        'PRAZO FINAL (DD/MM)': [
            '20/02',
            '25/03',
            '30/04'
        ],
        'TIPO DE ATO': [
            'PARECER',
            'PETIÇÃO',
            'PARECER'
        ],
        'DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)': [
            '15/02/2025',
            None,
            None
        ]
    }
    
    df = pd.DataFrame(data)
    filename = 'teste_processos.xlsx'
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"✅ Arquivo de exemplo criado: {filename}")
    return filename

def test_preview(filename):
    """Testa preview do upload."""
    print("\n📋 Testando preview...")
    
    # Login
    login_response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.text}")
        return None
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Preview
    with open(filename, "rb") as f:
        preview_response = requests.post(
            f"{API_URL}/api/processes/preview-upload",
            headers=headers,
            files={"file": f},
            params={"preview_rows": 20}
        )
    
    if preview_response.status_code == 200:
        preview_data = preview_response.json()
        print(f"✅ Preview OK")
        print(f"   Total de linhas: {preview_data.get('total_rows', 0)}")
        print(f"   Preview: {preview_data.get('preview_rows', 0)} linhas")
        print(f"   Válidas: {preview_data.get('summary', {}).get('valid', 0)}")
        print(f"   Erros: {preview_data.get('summary', {}).get('errors', 0)}")
        print(f"   Pode importar: {preview_data.get('can_import', False)}")
        return headers, preview_data.get('can_import', False)
    else:
        print(f"❌ Erro no preview: {preview_response.text}")
        return None, False

def test_upload(filename, headers):
    """Testa upload real."""
    print("\n📤 Testando upload...")
    
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        upload_response = requests.post(
            f"{API_URL}/processes/upload-excel",
            headers={k: v for k, v in headers.items() if k != "Content-Type"},  # Remove Content-Type para multipart
            files=files
        )
    
    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        print(f"✅ Upload OK")
        print(f"   Importados: {upload_data.get('imported', 0)}")
        print(f"   Ignorados: {upload_data.get('skipped', 0)}")
        print(f"   Erros: {upload_data.get('total_errors', 0)}")
        return True
    else:
        print(f"❌ Erro no upload: {upload_response.text}")
        return False

def main():
    """Função principal."""
    print("🧪 Teste de Upload de Planilha XLSX\n")
    
    # Criar arquivo de exemplo
    filename = create_example_file()
    
    # Testar preview
    result = test_preview(filename)
    if not result:
        print("\n❌ Falha no preview. Verifique se o servidor está rodando.")
        return
    
    headers, can_import = result
    
    if not can_import:
        print("\n⚠️  Preview indica que não é possível importar.")
        print("   Revise os erros acima antes de continuar.")
        print("   Pulando upload automático. Use o frontend para revisar erros.")
        return
    
    # Testar upload
    success = test_upload(filename, headers)
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        print(f"   Arquivo de teste: {filename}")
        print("   Você pode usar este arquivo como referência.")
    else:
        print("\n❌ Falha no upload.")

if __name__ == "__main__":
    main()
