"""
Importador de Excel para o Sistema PGR
Permite migrar dados de planilhas existentes para o banco de dados.
"""
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, date

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd  # noqa: E402
from backend.models_sqlalchemy import (  # noqa: E402
    get_engine, get_session, Process, ProcessType, Status
)


def parse_date(date_str) -> Optional[date]:
    """
    Converte diversos formatos de data para objeto date do Python.
    Aceita: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, objetos datetime do pandas.
    """
    if pd.isna(date_str) or date_str is None:
        return None
    
    # Se já é datetime do pandas
    if isinstance(date_str, (pd.Timestamp, datetime)):
        return date_str.date()
    
    # Se é string
    date_str = str(date_str).strip()
    if not date_str or date_str.lower() in ['nan', 'nat', '']:
        return None
    
    # Tentar vários formatos
    formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    print(f"⚠️  Aviso: Não foi possível converter a data '{date_str}'. Ignorando.")
    return None


def detect_column_mapping(df: pd.DataFrame) -> dict:
    """
    Detecta automaticamente quais colunas do Excel correspondem aos campos do sistema.
    Retorna um dicionário mapeando campo_sistema -> nome_coluna_excel.
    """
    # Possíveis nomes para cada campo (case-insensitive)
    field_aliases = {
        'protocol': ['protocolo', 'numero', 'processo', 'nº', 'numero processo', 'protocol'],
        'type': ['tipo', 'tipo processo', 'modalidade', 'type'],
        'applicant': ['requerente', 'servidor', 'nome', 'solicitante', 'applicant'],
        'registration': ['matricula', 'matrícula', 'siape', 'registration'],
        'status': ['status', 'situacao', 'situação', 'estado'],
        'created_date': ['data', 'data abertura', 'data criacao', 'data criação', 'created', 'abertura'],
        'financial_date': ['efeito financeiro', 'data efeito', 'efeito', 'financial'],
        'parecer': ['parecer', 'observacao', 'observação', 'obs', 'notes']
    }
    
    mapping = {}
    columns_lower = {col.lower(): col for col in df.columns}
    
    for field, aliases in field_aliases.items():
        for alias in aliases:
            if alias in columns_lower:
                mapping[field] = columns_lower[alias]
                break
    
    return mapping


def import_from_excel(excel_path: str, sheet_name: str | int = 0, dry_run: bool = False):
    """
    Importa processos de uma planilha Excel.
    
    Args:
        excel_path: Caminho para o arquivo .xlsx ou .xls
        sheet_name: Nome ou índice da aba (padrão: primeira aba)
        dry_run: Se True, apenas mostra o que seria importado sem salvar
    
    Formato esperado (colunas detectadas automaticamente):
    - Protocolo/Número: Número do processo (ex: PGR-2025-0005)
    - Tipo: PROM_CAP ou PROG_MER
    - Requerente: Nome do servidor
    - Matrícula: Opcional
    - Status: RECEBIDO, EM_ANALISE, PENDENTE_DOCS, etc.
    - Data/Abertura: Data de criação do processo
    - Efeito Financeiro: Opcional
    - Parecer: Opcional
    """
    print(f"\n{'='*60}")
    print("📊 IMPORTAÇÃO DE EXCEL - PGR")
    print(f"{'='*60}\n")
    
    # 1. Ler Excel
    print(f"📂 Lendo arquivo: {excel_path}")
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        print(f"✅ {len(df)} linhas encontradas\n")
    except Exception as e:
        print(f"❌ Erro ao ler Excel: {e}")
        return
    
    # 2. Detectar colunas
    print("🔍 Detectando colunas...")
    mapping = detect_column_mapping(df)
    
    if not mapping.get('protocol'):
        print("❌ ERRO: Coluna de protocolo não encontrada!")
        print(f"   Colunas disponíveis: {', '.join(df.columns)}")
        print("   Renomeie uma coluna para 'Protocolo' ou 'Numero'")
        return
    
    print("\n📋 Mapeamento de colunas:")
    for field, col in mapping.items():
        print(f"   • {field:15} -> {col}")
    
    if not mapping.get('type'):
        print("\n⚠️  Aviso: Coluna 'Tipo' não encontrada. Usando PROM_CAP como padrão.")
    if not mapping.get('applicant'):
        print("⚠️  Aviso: Coluna 'Requerente' não encontrada.")
    
    # 3. Conectar ao banco
    engine = get_engine()
    session = get_session(engine)
    
    # Carregar tipos e status disponíveis
    types_map = {t.code: t for t in session.query(ProcessType).all()}
    status_map = {s.code: s for s in session.query(Status).all()}
    
    print(f"\n📦 Tipos disponíveis: {', '.join(types_map.keys())}")
    print(f"📦 Status disponíveis: {', '.join(status_map.keys())}\n")
    
    # 4. Processar cada linha
    imported = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        protocol = None  # Inicializar para evitar UnboundLocalError
        try:
            # Obter valores das colunas mapeadas
            protocol = str(row[mapping['protocol']]).strip() if mapping.get('protocol') else None
            
            if not protocol or protocol.lower() in ['nan', 'none', '']:
                skipped += 1
                continue
            
            # Verificar se já existe
            existing = session.query(Process).filter_by(protocol_number=protocol).first()
            if existing:
                print(f"⏭️  {protocol}: Já existe, pulando...")
                skipped += 1
                continue
            
            # Tipo de processo
            type_code = None
            if mapping.get('type'):
                type_str = str(row[mapping['type']]).strip().upper()
                if 'CAPACITA' in type_str or 'CAP' in type_str:
                    type_code = 'PROM_CAP'
                elif 'MÉRITO' in type_str or 'MERIT' in type_str or 'MER' in type_str:
                    type_code = 'PROG_MER'
                else:
                    type_code = type_str if type_str in types_map else 'PROM_CAP'
            else:
                type_code = 'PROM_CAP'
            
            if type_code not in types_map:
                linha = int(idx) + 2 if isinstance(idx, (int, float)) else 0
                print(f"❌ {protocol}: Tipo '{type_code}' inválido")
                errors.append(f"Linha {linha}: Tipo '{type_code}' não existe")
                continue
            
            # Status
            status_code = 'RECEBIDO'
            if mapping.get('status'):
                status_str = str(row[mapping['status']]).strip().upper()
                # Tentar mapear variações
                status_variations = {
                    'RECEBIDO': 'RECEBIDO',
                    'EM ANALISE': 'EM_ANALISE',
                    'EM ANÁLISE': 'EM_ANALISE',
                    'PENDENTE': 'PENDENTE_DOCS',
                    'COMPLETO': 'COMPLETO',
                    'DEFERIDO': 'DEFERIDO',
                    'INDEFERIDO': 'INDEFERIDO',
                    'CANCELADO': 'CANCELADO'
                }
                status_code = status_variations.get(status_str, status_str)
                if status_code not in status_map:
                    status_code = 'RECEBIDO'
            
            # Requerente
            applicant = str(row[mapping['applicant']]).strip() if mapping.get('applicant') else 'Não informado'
            if applicant.lower() in ['nan', 'none', '']:
                applicant = 'Não informado'
            
            # Matrícula
            registration = None
            if mapping.get('registration'):
                reg = str(row[mapping['registration']]).strip()
                if reg.lower() not in ['nan', 'none', '']:
                    registration = reg
            
            # Datas
            created_date = parse_date(row[mapping['created_date']]) if mapping.get('created_date') else date.today()
            financial_date = parse_date(row[mapping['financial_date']]) if mapping.get('financial_date') else None
            
            # Parecer
            parecer = None
            if mapping.get('parecer'):
                par = str(row[mapping['parecer']]).strip()
                if par.lower() not in ['nan', 'none', '']:
                    parecer = par
            
            # Criar processo
            new_process = Process(
                protocol_number=protocol,
                type_id=types_map[type_code].id,
                status_id=status_map[status_code].id,
                applicant_name=applicant,
                applicant_registration=registration,
                created_date=created_date,
                financial_effective_date=financial_date,
                parecer=parecer
            )
            
            if dry_run:
                print(f"✓ {protocol} - {applicant} ({type_code}) [{status_code}]")
            else:
                session.add(new_process)
                session.flush()  # Para obter o ID
                
                # Criar checklist automático (igual ao endpoint POST)
                from backend.api_sqlalchemy import create_process_checklist, create_process_deadlines
                create_process_checklist(session, new_process.id, types_map[type_code].id)
                if created_date:
                    create_process_deadlines(session, new_process.id, types_map[type_code].id, created_date)
                
                print(f"✅ {protocol} - {applicant} (ID: {new_process.id})")
            
            imported += 1
            
        except Exception as e:
            linha = int(idx) + 2 if isinstance(idx, (int, float)) else 0
            errors.append(f"Linha {linha} ({protocol or '?'}): {str(e)}")
            print(f"❌ Erro na linha {linha}: {e}")
    
    # 5. Salvar ou mostrar resultado
    print(f"\n{'='*60}")
    if dry_run:
        print("🔍 MODO DE TESTE (nada foi salvo)")
        print(f"   ✓ {imported} processos seriam importados")
        print(f"   ⏭️  {skipped} processos seriam pulados")
    else:
        try:
            session.commit()
            print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"   ✓ {imported} processos importados")
            print(f"   ⏭️  {skipped} processos pulados (já existem)")
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao salvar no banco: {e}")
            return
    
    if errors:
        print(f"\n⚠️  {len(errors)} erros encontrados:")
        for err in errors[:10]:  # Mostrar no máximo 10
            print(f"   • {err}")
        if len(errors) > 10:
            print(f"   ... e mais {len(errors) - 10} erros")
    
    print(f"{'='*60}\n")
    session.close()


def create_template():
    """
    Cria uma planilha modelo para importação.
    """
    template_data = {
        'Protocolo': ['PGR-2025-0020', 'PGR-2025-0021', 'PGR-2025-0022'],
        'Tipo': ['PROM_CAP', 'PROG_MER', 'PROM_CAP'],
        'Requerente': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
        'Matrícula': ['123456', '789012', '345678'],
        'Status': ['RECEBIDO', 'EM_ANALISE', 'RECEBIDO'],
        'Data': ['19/12/2025', '15/12/2025', '18/12/2025'],
        'Efeito Financeiro': ['01/01/2026', '', '01/02/2026'],
        'Parecer': ['', 'Em análise pela comissão', '']
    }
    
    df = pd.DataFrame(template_data)
    output_path = 'template_importacao.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Processos')
    
    print(f"✅ Template criado: {output_path}")
    print("\n📋 Instruções:")
    print("   1. Preencha os dados dos processos")
    print("   2. Salve o arquivo")
    print("   3. Execute: python import_excel.py seu_arquivo.xlsx")
    print("\n📌 Colunas obrigatórias: Protocolo, Tipo, Requerente")
    print("📌 Tipos válidos: PROM_CAP, PROG_MER")
    print("📌 Status válidos: RECEBIDO, EM_ANALISE, PENDENTE_DOCS, COMPLETO, DEFERIDO, INDEFERIDO, CANCELADO")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🏛️  IMPORTADOR DE EXCEL - SISTEMA PGR")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\n📖 USO:")
        print("   python import_excel.py seu_arquivo.xlsx          # Importar")
        print("   python import_excel.py seu_arquivo.xlsx --test   # Testar sem salvar")
        print("   python import_excel.py --template                # Criar template")
        print("\n💡 DICA: Execute com --test primeiro para validar os dados!\n")
        sys.exit(1)
    
    if sys.argv[1] == '--template':
        create_template()
    else:
        excel_file = sys.argv[1]
        dry_run = '--test' in sys.argv or '--dry-run' in sys.argv
        
        import_from_excel(excel_file, dry_run=dry_run)
