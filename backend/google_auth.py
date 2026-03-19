"""
Google API Authentication using Service Account.
"""
import os
from pathlib import Path
from typing import Optional
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.auth

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',  # Para criar arquivos
    'https://www.googleapis.com/auth/spreadsheets'  # Para escrever em Sheets
]

_credentials: Optional[service_account.Credentials] = None


def get_credentials() -> service_account.Credentials:
    """
    Get or create Google Service Account credentials.
    
    Returns:
        Service account credentials object
        
    Raises:
        FileNotFoundError: If credentials file not found
        ValueError: If credentials are invalid
    """
    global _credentials
    
    if _credentials and _credentials.valid:
        return _credentials
    
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    if not credentials_path:
        credentials_path = Path(__file__).parent.parent / 'credentials' / 'service_account.json'
    
    credentials_path = Path(credentials_path)
    
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Google Service Account credentials not found at {credentials_path}. "
            "Set GOOGLE_CREDENTIALS_PATH environment variable or place credentials at "
            "credentials/service_account.json"
        )
    
    try:
        _credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=SCOPES
        )
        
        if not _credentials.valid:
            _credentials.refresh(Request())
        
        return _credentials
    except Exception as e:
        raise ValueError(f"Failed to load Google credentials: {str(e)}")


def get_authenticated_session():
    """
    Get authenticated requests session for Google APIs.
    
    Returns:
        Authenticated requests session
    """
    credentials = get_credentials()
    return credentials.authorize(google.auth.transport.requests.Request())


def get_service_account_email() -> str:
    """
    Get Service Account email address.
    
    This email should be shared with Google Sheets for access.
    
    Returns:
        Service Account email address
        
    Raises:
        ValueError: If credentials cannot be loaded
    """
    try:
        credentials = get_credentials()
        return credentials.service_account_email
    except Exception as e:
        raise ValueError(f"Failed to get Service Account email: {str(e)}")
