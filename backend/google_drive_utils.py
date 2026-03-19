"""
Utilitários para download de arquivos do Google Drive e Google Sheets.
"""
import re
import io
import requests
from typing import Tuple, Optional


def extract_file_id_from_url(url: str) -> Optional[str]:
    """
    Extrai o FILE_ID de uma URL do Google Drive ou Google Sheets.
    
    Suporta os seguintes formatos:
    - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    - https://drive.google.com/open?id=FILE_ID
    - https://docs.google.com/spreadsheets/d/FILE_ID/edit?usp=sharing
    - https://docs.google.com/spreadsheets/d/FILE_ID/edit#gid=0
    """
    # Padrões para extrair FILE_ID
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'/open\?id=([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'/document/d/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def is_google_sheets_url(url: str) -> bool:
    """Verifica se a URL é do Google Sheets."""
    return 'docs.google.com/spreadsheets' in url or '/spreadsheets/d/' in url


def is_google_drive_url(url: str) -> bool:
    """Verifica se a URL é do Google Drive ou Google Sheets."""
    return 'drive.google.com' in url or 'docs.google.com' in url


def download_from_google_drive(url: str) -> Tuple[bytes, str]:
    """
    Baixa um arquivo do Google Drive ou Google Sheets.
    
    Args:
        url: URL do Google Drive ou Google Sheets
        
    Returns:
        Tuple com (conteúdo do arquivo em bytes, nome do arquivo sugerido)
        
    Raises:
        ValueError: Se a URL não for válida
        requests.RequestException: Se houver erro no download
    """
    file_id = extract_file_id_from_url(url)
    
    if not file_id:
        raise ValueError("Não foi possível extrair o ID do arquivo da URL fornecida")
    
    # Se for Google Sheets, usar endpoint de export
    if is_google_sheets_url(url):
        download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        filename = "planilha_google_sheets.xlsx"
    else:
        # Para arquivos do Google Drive, tentar download direto
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        filename = "arquivo_google_drive.xlsx"
    
    # Fazer download
    session = requests.Session()
    response = session.get(download_url, timeout=30)
    response.raise_for_status()
    
    # Verificar se é um arquivo válido (não HTML de erro)
    content_type = response.headers.get('Content-Type', '')
    # Para Google Sheets, o content-type geralmente é application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    # Se for HTML, provavelmente é uma página de erro
    if 'text/html' in content_type:
        # Tentar método alternativo para arquivos grandes do Drive
        if not is_google_sheets_url(url):
            confirm_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
            response = session.get(confirm_url, timeout=30)
            response.raise_for_status()
            
            # Verificar novamente
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                raise ValueError(
                    "Arquivo não encontrado ou não está compartilhado publicamente. "
                    "Certifique-se de que o link está acessível para 'Qualquer pessoa com o link'."
                )
        else:
            raise ValueError(
                "Planilha não encontrada ou não está compartilhada publicamente. "
                "Certifique-se de que a planilha está compartilhada como 'Qualquer pessoa com o link pode ver'."
            )
    
    content = response.content
    
    # Tentar detectar nome do arquivo do header
    content_disposition = response.headers.get('Content-Disposition', '')
    if 'filename=' in content_disposition:
        filename_match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if filename_match:
            filename = filename_match.group(1)
    
    return content, filename

