"""
Format-agnostic spreadsheet ingestion.
Supports XLSX, Google Sheets, CSV while preserving DOCX canonical schema.

DEPRECATED: Use spreadsheet_ingestion.py instead.
This module is kept for backward compatibility.
"""
import io
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from . import spreadsheet_ingestion


def read_spreadsheet(file_content: bytes, filename: str, file_format: Optional[str] = None) -> pd.DataFrame:
    """Delegate to spreadsheet_ingestion module."""
    return spreadsheet_ingestion.read_spreadsheet(file_content, filename, file_format)


def _detect_format(filename: str, content: bytes) -> str:
    """Delegate to spreadsheet_ingestion module."""
    return spreadsheet_ingestion._detect_format(filename, content)


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame for processing."""
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(['nan', 'None', 'NaT', ''], '')
    return df


def map_columns_to_docx_schema(df: pd.DataFrame) -> Tuple[Dict[str, str], List[str]]:
    """Map spreadsheet columns to DOCX canonical schema."""
    col_map = spreadsheet_ingestion.map_headers_to_canonical(df)
    is_valid, missing = spreadsheet_ingestion.validate_required_headers(col_map)
    
    missing_docx_names = []
    for missing_header in missing:
        missing_docx_names.append(missing_header)
    
    return col_map, missing_docx_names


def extract_process_row(row: pd.Series, col_map: Dict[str, str]) -> Dict[str, Optional[str]]:
    """Extract process data from a single row using canonical mapping."""
    return spreadsheet_ingestion.extract_row_data(row, col_map)


def validate_process_data(process_data: Dict[str, Optional[str]]) -> Tuple[bool, Optional[str]]:
    """Validate that process data has at least one identifier."""
    processo_adm = process_data.get('processo_adm_1doc')
    processo_judicial = process_data.get('processo_judicial')
    
    if not processo_adm and not processo_judicial:
        return False, "É necessário fornecer PROCESSO ADM 1DOC ou PROCESSO JUDICIAL"
    
    return True, None


def ingest_spreadsheet(
    file_content: bytes,
    filename: str,
    file_format: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    """Ingest spreadsheet in any supported format."""
    return spreadsheet_ingestion.ingest_spreadsheet(file_content, filename, file_format)
