"""
Format-agnostic spreadsheet ingestion layer.
Supports XLSX, Google Sheets, and CSV with canonical header mapping.
"""
import io
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any


# Canonical headers (exact match, case-insensitive)
CANONICAL_HEADERS = {
    'PROCESSO ADM 1DOC': 'processo_adm_1doc',
    'PROCESSO JUDICIAL': 'processo_judicial',
    'PARTES': 'partes',
    'DATA RECEBIMENTO (MÊS/ANO)': 'data_recebimento_mes_ano',
    'TEMA – OBSERVAÇÕES': 'tema_observacoes',
    'PRAZO INFO – ESTAG (DIA/MÊS)': 'prazo_info_estag',
    'PRAZO FINAL (DD/MM)': 'prazo_final',
    'TIPO DE ATO': 'tipo_ato',
    'DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)': 'data_realizacao_ato',
}

# Alternative header variations (for flexibility)
HEADER_VARIANTS = {
    'DATA DE REALIZAÇÃO DO ATO': 'data_realizacao_ato',
    'DATA DE REALIZAÇÃO DO ATO (DD/MM/AAAA)': 'data_realizacao_ato',
    'TIPO DE ATO (PETIÇÃO OU PARECER OU SEM ATO)': 'tipo_ato',
}

# Required headers (at least one identifier must be present)
REQUIRED_HEADERS = ['PROCESSO ADM 1DOC', 'PROCESSO JUDICIAL']

# Cabeçalhos alternativos comuns (planilhas de exemplo / exportações internas).
# Só aplicados se o campo canônico correspondente ainda não foi mapeado.
HEADER_FIELD_ALIAS_PAIRS: List[Tuple[str, str]] = [
    ('PROTOCOLO', 'processo_adm_1doc'),
    ('NUMERO PROTOCOLO', 'processo_adm_1doc'),
    ('NÚMERO PROTOCOLO', 'processo_adm_1doc'),
    ('NUMERO PROCESSO', 'processo_adm_1doc'),
    ('NÚMERO PROCESSO', 'processo_adm_1doc'),
    ('NUMERO_PROCESSO', 'processo_adm_1doc'),
    ('NÚMERO_PROCESSO', 'processo_adm_1doc'),
    ('REQUERENTE', 'partes'),
    ('MATRICULA', 'applicant_registration'),
    ('MATRÍCULA', 'applicant_registration'),
    ('DATA CRIACAO', 'data_recebimento_mes_ano'),
    ('DATA CRIAÇÃO', 'data_recebimento_mes_ano'),
    ('TIPO', 'tipo_ato'),
    ('STATUS', 'notes'),
]


def read_spreadsheet(file_content: bytes, filename: str, file_format: Optional[str] = None) -> pd.DataFrame:
    """
    Read spreadsheet from bytes, auto-detecting format.
    
    Supports: XLSX, CSV, Google Sheets (exported as XLSX)
    
    Args:
        file_content: File content as bytes
        filename: Original filename (for format detection)
        file_format: Optional explicit format ('xlsx', 'csv', 'google_sheets')
        
    Returns:
        pandas DataFrame with raw data
        
    Raises:
        ValueError: If format cannot be determined or file cannot be read
    """
    if file_format:
        fmt = file_format.lower()
        # Tipos do Google Drive (drive_service) → leitor pandas
        if fmt == 'excel':
            fmt = 'xlsx'
    else:
        fmt = _detect_format(filename, file_content)
    
    try:
        if fmt == 'csv':
            try:
                df = pd.read_csv(
                    io.BytesIO(file_content),
                    encoding='utf-8-sig',
                    dtype=str,
                    keep_default_na=False,
                    on_bad_lines='skip'
                )
            except TypeError:
                df = pd.read_csv(
                    io.BytesIO(file_content),
                    encoding='utf-8-sig',
                    dtype=str,
                    keep_default_na=False,
                    error_bad_lines=False
                )
        elif fmt == 'tsv':
            try:
                df = pd.read_csv(
                    io.BytesIO(file_content),
                    encoding='utf-8-sig',
                    sep='\t',
                    dtype=str,
                    keep_default_na=False,
                    on_bad_lines='skip',
                )
            except TypeError:
                df = pd.read_csv(
                    io.BytesIO(file_content),
                    encoding='utf-8-sig',
                    sep='\t',
                    dtype=str,
                    keep_default_na=False,
                    error_bad_lines=False,
                )
        elif fmt == 'xls':
            # Excel 97–2003: openpyxl não lê .xls
            df = pd.read_excel(
                io.BytesIO(file_content),
                dtype=str,
                keep_default_na=False,
                engine='xlrd',
            )
        elif fmt in ('xlsx', 'google_sheets'):
            df = pd.read_excel(
                io.BytesIO(file_content),
                dtype=str,
                keep_default_na=False,
                engine='openpyxl',
            )
        else:
            raise ValueError(f"Formato não suportado: {fmt}")
        
        return df
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo {fmt}: {str(e)}")


def _detect_format(filename: str, content: bytes) -> str:
    """
    Detect file format from filename and content signature.
    
    Returns:
        Format string: 'csv', 'xlsx', 'xls', 'google_sheets'
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.csv'):
        return 'csv'
    elif filename_lower.endswith('.xlsx'):
        return 'xlsx'
    elif filename_lower.endswith('.xls'):
        return 'xls'
    elif 'google' in filename_lower or 'sheets' in filename_lower:
        return 'google_sheets'
    else:
        if len(content) > 2 and content[:2] == b'PK':
            return 'xlsx'
        elif len(content) > 0 and (b',' in content[:1000] or b';' in content[:1000]):
            return 'csv'
        else:
            return 'xlsx'


def normalize_column_name(col_name: str) -> str:
    """
    Normalize column name for case-insensitive matching.
    Preserves legal semantics, only normalizes whitespace and case.
    
    Args:
        col_name: Original column name
        
    Returns:
        Normalized uppercase string with single spaces
    """
    if pd.isna(col_name):
        return ''
    return ' '.join(str(col_name).strip().upper().split())


def map_headers_to_canonical(df: pd.DataFrame) -> Dict[str, str]:
    """
    Map spreadsheet column headers to canonical field names.
    
    - Case-insensitive matching
    - Ignores column order
    - Ignores extra columns
    - Handles header variations
    
    Args:
        df: DataFrame with spreadsheet data
        
    Returns:
        Dictionary mapping canonical field names to original column names
        Example: {'processo_adm_1doc': 'Processo ADM 1DOC', ...}
    """
    col_map = {}
    normalized_headers = {}
    
    for col in df.columns:
        normalized = normalize_column_name(col)
        normalized_headers[normalized] = col
    
    for canonical_header, field_name in CANONICAL_HEADERS.items():
        normalized_canonical = normalize_column_name(canonical_header)
        
        if normalized_canonical in normalized_headers:
            col_map[field_name] = normalized_headers[normalized_canonical]
        else:
            for variant, variant_field in HEADER_VARIANTS.items():
                if variant_field == field_name:
                    normalized_variant = normalize_column_name(variant)
                    if normalized_variant in normalized_headers:
                        col_map[field_name] = normalized_headers[normalized_variant]
                        break

    # Sinônimos (ex.: coluna "Protocolo" → processo_adm_1doc)
    for alias_text, field_name in HEADER_FIELD_ALIAS_PAIRS:
        if field_name in col_map:
            continue
        na = normalize_column_name(alias_text)
        if na in normalized_headers:
            col_map[field_name] = normalized_headers[na]
    
    return col_map


def validate_required_headers(col_map: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate that required headers are present.
    
    At least one identifier header must be present:
    - PROCESSO ADM 1DOC
    - PROCESSO JUDICIAL
    
    Args:
        col_map: Column mapping dictionary
        
    Returns:
        Tuple of (is_valid, missing_headers)
        - is_valid: True if at least one required header is present
        - missing_headers: List of missing required header names
    """
    has_adm = 'processo_adm_1doc' in col_map
    has_judicial = 'processo_judicial' in col_map
    
    if has_adm or has_judicial:
        return True, []
    
    return False, REQUIRED_HEADERS


def extract_row_data(row: pd.Series, col_map: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    Extract process data from a single row.
    
    - Preserves partial dates as strings (no date parsing)
    - Handles empty cells as None
    - Preserves legal semantics
    
    Args:
        row: DataFrame row (pandas Series)
        col_map: Column mapping dictionary
        
    Returns:
        Dictionary with canonical field names and string values (or None)
    """
    data = {}
    
    for field_name, col_name in col_map.items():
        if col_name in row.index:
            value = row[col_name]
            
            if pd.isna(value) or value == '' or str(value).strip() == '':
                data[field_name] = None
            else:
                value_str = str(value).strip()
                data[field_name] = value_str if value_str else None
        else:
            data[field_name] = None
    
    return data


def ingest_spreadsheet(
    file_content: bytes,
    filename: str,
    file_format: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    """
    Ingest spreadsheet in any supported format.
    
    Process:
    1. Read file (XLSX, CSV, or Google Sheets)
    2. Normalize column headers
    3. Map headers to canonical schema
    4. Validate required headers
    5. Return DataFrame and mapping
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        file_format: Optional explicit format
        
    Returns:
        Tuple of:
        - DataFrame: Normalized spreadsheet data
        - col_map: Dictionary mapping canonical fields to original columns
        - missing_headers: List of missing required header names
        
    Raises:
        ValueError: If file cannot be read or required headers are missing
    """
    df = read_spreadsheet(file_content, filename, file_format)
    
    if df.empty:
        raise ValueError("Planilha vazia")
    
    col_map = map_headers_to_canonical(df)
    is_valid, missing = validate_required_headers(col_map)
    
    if not is_valid:
        missing_names = ', '.join(missing)
        raise ValueError(
            f"Colunas obrigatórias não encontradas: {missing_names}. "
            f"É necessário pelo menos uma das seguintes colunas: PROCESSO ADM 1DOC ou PROCESSO JUDICIAL."
        )
    
    return df, col_map, missing


def process_spreadsheet_rows(
    df: pd.DataFrame,
    col_map: Dict[str, str]
) -> List[Dict[str, Optional[str]]]:
    """
    Process all rows in spreadsheet, extracting canonical data.
    
    Args:
        df: DataFrame with spreadsheet data
        col_map: Column mapping dictionary
        
    Returns:
        List of dictionaries, one per row, with canonical field names
    """
    rows_data = []
    
    for idx, row in df.iterrows():
        row_data = extract_row_data(row, col_map)
        rows_data.append(row_data)
    
    return rows_data


def validate_row_data(
    row_data: Dict[str, Optional[str]],
    row_number: int,
    db_session = None
) -> Dict[str, Any]:
    """
    Validate a single row of process data.
    
    Returns validation result with:
    - status: 'valid', 'warning', 'error'
    - errors: List of critical errors (block import)
    - warnings: List of warnings (allow import but notify)
    - row_number: Original row number in spreadsheet
    
    Args:
        row_data: Extracted row data with canonical field names
        row_number: Row number in spreadsheet (1-indexed, including header)
        db_session: Optional database session for duplicate checking
        
    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []
    
    processo_adm = row_data.get('processo_adm_1doc')
    processo_judicial = row_data.get('processo_judicial')
    
    if not processo_adm and not processo_judicial:
        errors.append({
            "field": "identificador",
            "message": "É obrigatório informar PROCESSO ADM 1DOC ou PROCESSO JUDICIAL",
            "severity": "error"
        })
    
    if processo_adm:
        processo_adm_clean = str(processo_adm).strip() if processo_adm else None
        if processo_adm_clean:
            if db_session:
                from . import models_sqlalchemy as models
                existing = db_session.query(models.Process).filter(
                    models.Process.processo_adm_1doc == processo_adm_clean
                ).first()
                if existing:
                    warnings.append({
                        "field": "processo_adm_1doc",
                        "message": f"Processo administrativo {processo_adm_clean} já existe no sistema. Será ignorado na importação.",
                        "severity": "warning"
                    })
    
    if processo_judicial:
        processo_judicial_clean = str(processo_judicial).strip() if processo_judicial else None
        if processo_judicial_clean:
            if db_session:
                from . import models_sqlalchemy as models
                existing = db_session.query(models.Process).filter(
                    models.Process.processo_judicial == processo_judicial_clean
                ).first()
                if existing:
                    warnings.append({
                        "field": "processo_judicial",
                        "message": f"Processo judicial {processo_judicial_clean} já existe no sistema. Será ignorado na importação.",
                        "severity": "warning"
                    })
    
    if not processo_adm and not processo_judicial:
        status = 'error'
    elif errors:
        status = 'error'
    elif warnings:
        status = 'warning'
    else:
        status = 'valid'
    
    return {
        "row_number": row_number,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "data": row_data
    }


def preview_spreadsheet(
    file_content: bytes,
    filename: str,
    file_format: Optional[str] = None,
    preview_rows: int = 20,
    db_session = None
) -> Dict[str, Any]:
    """
    Generate preview and validation for spreadsheet without importing.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        file_format: Optional explicit format
        preview_rows: Number of rows to preview (default 20)
        db_session: Optional database session for duplicate checking
        
    Returns:
        Dictionary with:
        - total_rows: Total number of data rows
        - preview_rows: Number of rows in preview
        - column_mapping: Mapping of canonical fields to original columns
        - preview: List of validated row previews
        - summary: Summary statistics
        - can_import: Whether import is allowed (no critical errors)
    """
    try:
        df, col_map, missing = ingest_spreadsheet(file_content, filename, file_format)
    except ValueError as e:
        return {
            "error": str(e),
            "can_import": False
        }
    except Exception as e:
        return {
            "error": f"Erro ao processar planilha: {str(e)}",
            "can_import": False
        }
    
    total_rows = len(df)
    preview_count = min(preview_rows, total_rows)
    
    preview_data = []
    error_count = 0
    warning_count = 0
    valid_count = 0
    
    for idx in range(preview_count):
        row = df.iloc[idx]
        row_data = extract_row_data(row, col_map)
        validation = validate_row_data(row_data, idx + 2, db_session)
        
        preview_data.append(validation)
        
        if validation['status'] == 'error':
            error_count += 1
        elif validation['status'] == 'warning':
            warning_count += 1
        else:
            valid_count += 1
    
    can_import = error_count == 0
    
    return {
        "filename": filename,
        "total_rows": total_rows,
        "preview_rows": preview_count,
        "column_mapping": {
            field: col for field, col in col_map.items()
        },
        "preview": preview_data,
        "summary": {
            "total": preview_count,
            "valid": valid_count,
            "warnings": warning_count,
            "errors": error_count
        },
        "can_import": can_import,
        "message": (
            f"Encontrados {error_count} erro(s) crítico(s) que impedem a importação."
            if error_count > 0 else
            f"Preview gerado com sucesso. {valid_count} linha(s) válida(s), {warning_count} aviso(s)."
        )
    }


def template_column_headers() -> List[str]:
    """Cabeçalhos na ordem canónica aceite pelo importador."""
    return list(CANONICAL_HEADERS.keys())


def build_process_spreadsheet_template(
    file_format: str = "xlsx",
    include_example_row: bool = False,
) -> Tuple[bytes, str, str]:
    """
    Gera ficheiro vazio (ou com uma linha de exemplo) para o cliente preencher.

    Args:
        file_format: 'xlsx' ou 'csv'
        include_example_row: Se True, inclui uma linha ilustrativa (deve apagar/alterar)

    Returns:
        (conteúdo em bytes, media_type, nome_ficheiro sugerido)
    """
    columns = template_column_headers()
    rows: List[List[Any]] = []
    if include_example_row:
        rows.append([
            "EXEMPLO-ADM-2026-0001",
            "",
            "Requerente A / Requerente B",
            "JAN/2026",
            "Tema ou observações resumidas",
            "10/02",
            "15/03",
            "PETIÇÃO",
            "01/02/2026",
        ])
    df = pd.DataFrame(rows, columns=columns)
    buf = io.BytesIO()
    fmt = (file_format or "xlsx").lower().strip()
    if fmt == "csv":
        df.to_csv(buf, index=False, encoding="utf-8-sig")
        buf.seek(0)
        return (
            buf.getvalue(),
            "text/csv; charset=utf-8",
            "PGR_modelo_processos.csv",
        )
    if fmt != "xlsx":
        raise ValueError("Formato deve ser 'xlsx' ou 'csv'")
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return (
        buf.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "PGR_modelo_processos.xlsx",
    )
