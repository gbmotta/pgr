"""
Google Sheets API service for fetching spreadsheet data.
"""
import io
import pandas as pd
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from . import google_auth
from . import google_drive_utils


def get_sheets_service():
    """
    Get authenticated Google Sheets API service.
    
    Returns:
        Google Sheets API service object
    """
    credentials = google_auth.get_credentials()
    return build('sheets', 'v4', credentials=credentials)


def fetch_sheet_data(file_id: str, range_name: Optional[str] = None) -> List[List[Any]]:
    """
    Fetch data from Google Sheets.
    
    Args:
        file_id: Google Sheets file ID
        range_name: Optional range (e.g., 'Sheet1!A1:Z1000'). If None, fetches all data.
        
    Returns:
        List of rows, each row is a list of cell values
        
    Raises:
        HttpError: If API call fails
        ValueError: If file_id is invalid
    """
    try:
        service = get_sheets_service()
        spreadsheet = service.spreadsheets()
        
        if range_name:
            result = spreadsheet.values().get(
                spreadsheetId=file_id,
                range=range_name
            ).execute()
        else:
            result = spreadsheet.values().get(
                spreadsheetId=file_id,
                range='A:Z'
            ).execute()
        
        values = result.get('values', [])
        return values
    except HttpError as e:
        raise ValueError(f"Failed to fetch Google Sheets data: {str(e)}")


def fetch_sheet_as_dataframe(file_id: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch Google Sheets data as pandas DataFrame.
    
    Args:
        file_id: Google Sheets file ID
        sheet_name: Optional sheet name. If None, uses first sheet.
        
    Returns:
        pandas DataFrame with sheet data
        
    Raises:
        ValueError: If data cannot be fetched or parsed
    """
    try:
        range_name = f"{sheet_name}!A:Z" if sheet_name else None
        values = fetch_sheet_data(file_id, range_name)
        
        if not values:
            return pd.DataFrame()
        
        df = pd.DataFrame(values[1:], columns=values[0] if values else [])
        return df
    except Exception as e:
        raise ValueError(f"Failed to convert Sheets data to DataFrame: {str(e)}")


def fetch_sheet_as_excel_bytes(file_id: str) -> bytes:
    """
    Fetch Google Sheets as Excel bytes (for compatibility with existing code).
    
    Args:
        file_id: Google Sheets file ID
        
    Returns:
        Excel file content as bytes
    """
    try:
        df = fetch_sheet_as_dataframe(file_id)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        return output.read()
    except Exception as e:
        raise ValueError(f"Failed to export Sheets as Excel: {str(e)}")


def process_sheet_data(file_id: str, db, import_logic) -> Dict[str, Any]:
    """
    Process Google Sheets data using existing import logic.
    
    Args:
        file_id: Google Sheets file ID
        db: Database session
        import_logic: Function that processes DataFrame and returns import results
        
    Returns:
        Dictionary with import results
    """
    try:
        df = fetch_sheet_as_dataframe(file_id)
        
        if df.empty:
            return {
                "imported": 0,
                "skipped": 0,
                "errors": ["Planilha vazia"],
                "total_errors": 1
            }
        
        return import_logic(df, db)
    except Exception as e:
        return {
            "imported": 0,
            "skipped": 0,
            "errors": [str(e)],
            "total_errors": 1
        }
