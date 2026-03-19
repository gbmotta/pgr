"""
Google Sheets column mapping to DOCX canonical schema.
Maps exact column names from DOCX table to database fields.
"""
from typing import Dict, Optional, Tuple, List
import pandas as pd


DOCX_COLUMN_MAPPING = {
    # Exact column names from DOCX table
    'PROCESSO ADM 1DOC': 'processo_adm_1doc',
    'PROCESSO JUDICIAL': 'processo_judicial',
    'PARTES': 'partes',
    'DATA RECEBIMENTO (MÊS/ANO)': 'data_recebimento_mes_ano',
    'TEMA – OBSERVAÇÕES': 'tema_observacoes',
    'PRAZO INFO – ESTAG (DIA/MÊS)': 'prazo_info_estag',
    'PRAZO FINAL (DD/MM)': 'prazo_final',
    'TIPO DE ATO (PETIÇÃO OU PARECER OU SEM ATO)': 'tipo_ato',
    'TIPO DE ATO': 'tipo_ato',
    'DATA DE REALIZAÇÃO DO ATO (DD/MM/AAAA)': 'data_realizacao_ato',
    'DATA DE REALIZAÇÃO DO ATO': 'data_realizacao_ato',
}


def normalize_column_name(col_name: str) -> str:
    """
    Normalize column name for matching.
    Removes extra spaces, converts to uppercase, handles variations.
    """
    if pd.isna(col_name):
        return ''
    col_str = str(col_name).strip()
    return col_str.upper()


def map_sheet_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Map Google Sheets columns to DOCX canonical schema.
    
    Args:
        df: DataFrame with sheet data
        
    Returns:
        Dictionary mapping canonical field names to original column names
    """
    col_map = {}
    
    for col in df.columns:
        normalized = normalize_column_name(col)
        
        for docx_col, field_name in DOCX_COLUMN_MAPPING.items():
            if normalized == docx_col.upper() or normalized.startswith(docx_col.upper()):
                if field_name not in col_map:
                    col_map[field_name] = col
                break
    
    return col_map


def extract_process_data(row: pd.Series, col_map: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    Extract process data from sheet row using canonical mapping.
    
    Args:
        row: DataFrame row
        col_map: Column mapping dictionary
        
    Returns:
        Dictionary with canonical field names and values
    """
    data = {}
    
    for field_name, col_name in col_map.items():
        if col_name in row.index:
            value = row[col_name]
            if pd.isna(value):
                data[field_name] = None
            else:
                data[field_name] = str(value).strip() if value else None
        else:
            data[field_name] = None
    
    return data


def validate_required_columns(col_map: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate that at least one identifier column is present.
    At least PROCESSO ADM 1DOC or PROCESSO JUDICIAL must be present.
    
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    has_adm = 'processo_adm_1doc' in col_map
    has_judicial = 'processo_judicial' in col_map
    
    if has_adm or has_judicial:
        return True, []
    
    return False, ['PROCESSO ADM 1DOC ou PROCESSO JUDICIAL']
