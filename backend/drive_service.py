"""
Google Drive API service for watch channels and change notifications.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from . import google_auth


def get_drive_service():
    """
    Get authenticated Google Drive API service.
    
    Returns:
        Google Drive API service object
    """
    credentials = google_auth.get_credentials()
    return build('drive', 'v3', credentials=credentials)


def create_watch_channel(
    file_id: str,
    webhook_url: str,
    expiration_hours: int = 168
) -> Dict[str, Any]:
    """
    Create a watch channel for a Google Drive file.
    
    Args:
        file_id: Google Drive file ID
        webhook_url: Public URL to receive change notifications
        expiration_hours: Channel expiration in hours (default: 7 days)
        
    Returns:
        Dictionary with channel information (id, resource_id, expiration)
        
    Raises:
        HttpError: If API call fails
        ValueError: If parameters are invalid
    """
    try:
        service = get_drive_service()
        
        channel_id = str(uuid.uuid4())
        expiration = int((datetime.utcnow() + timedelta(hours=expiration_hours)).timestamp() * 1000)
        
        request_body = {
            'id': channel_id,
            'type': 'web_hook',
            'address': webhook_url,
            'expiration': expiration
        }
        
        response = service.files().watch(
            fileId=file_id,
            body=request_body
        ).execute()
        
        return {
            'channel_id': response.get('id'),
            'resource_id': response.get('resourceId'),
            'expiration': response.get('expiration'),
            'file_id': file_id
        }
    except HttpError as e:
        raise ValueError(f"Failed to create watch channel: {str(e)}")


def stop_watch_channel(resource_id: str) -> bool:
    """
    Stop a watch channel.
    
    Args:
        resource_id: Channel resource ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        service = get_drive_service()
        service.channels().stop(body={'id': resource_id}).execute()
        return True
    except HttpError:
        return False


def get_file_metadata(file_id: str) -> Dict[str, Any]:
    """
    Get file metadata from Google Drive.
    
    Args:
        file_id: Google Drive file ID
        
    Returns:
        Dictionary with file metadata
        
    Raises:
        HttpError: If API call fails
    """
    try:
        service = get_drive_service()
        file_metadata = service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,modifiedTime,size'
        ).execute()
        
        return file_metadata
    except HttpError as e:
        raise ValueError(f"Failed to get file metadata: {str(e)}")


def verify_file_exists(file_id: str) -> bool:
    """
    Verify if a file exists and is accessible.
    
    Args:
        file_id: Google Drive file ID
        
    Returns:
        True if file exists and is accessible, False otherwise
    """
    try:
        get_file_metadata(file_id)
        return True
    except (HttpError, ValueError):
        return False


def verify_file_access(file_id: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Verify if Service Account has access to a file.
    
    Args:
        file_id: Google Drive file ID
        
    Returns:
        Tuple of (has_access: bool, file_name: Optional[str], error_message: Optional[str], file_type: Optional[str])
        - If has_access is True: file_name contains the file name, error_message is None, file_type is 'google_sheets', 'excel', 'csv', or 'tsv'
        - If has_access is False: file_name is None, error_message contains user-friendly error, file_type is None
    """
    try:
        metadata = get_file_metadata(file_id)
        file_name = metadata.get('name', 'Unknown')
        mime_type = metadata.get('mimeType', '')
        
        # Verificar tipos de arquivo suportados
        # Google Sheets nativo
        if mime_type == 'application/vnd.google-apps.spreadsheet':
            return True, file_name, None, 'google_sheets'
        
        # Excel
        is_excel = mime_type in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'application/excel'
        ]
        if is_excel or file_name.lower().endswith(('.xlsx', '.xls')):
            return True, file_name, None, 'excel'
        
        # CSV
        is_csv = mime_type in [
            'text/csv',
            'application/csv'
        ] or file_name.lower().endswith('.csv')
        if is_csv:
            return True, file_name, None, 'csv'
        
        # TSV
        is_tsv = mime_type in [
            'text/tab-separated-values',
            'text/tsv'
        ] or file_name.lower().endswith('.tsv')
        if is_tsv:
            return True, file_name, None, 'tsv'
        
        # Arquivo não suportado
        if True:  # else case
            service_account_email = None
            try:
                from . import google_auth
                service_account_email = google_auth.get_service_account_email()
            except:
                pass
            
            # Detectar se é um arquivo Excel
            is_excel = mime_type in [
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel',
                'application/excel'
            ]
            
            error_msg = (
                f"O arquivo '{file_name}' não é um formato suportado.\n"
                f"Tipo detectado: {mime_type}\n\n"
                "Formatos suportados: Google Sheets, Excel (.xlsx, .xls), CSV, TSV"
            )
            
            if service_account_email:
                error_msg += f"\n\nEmail do Service Account: {service_account_email}"
            
            return False, None, error_msg, None
    except HttpError as e:
        error_code = e.resp.status if hasattr(e, 'resp') else None
        
        if error_code == 404:
            return False, None, "Arquivo não encontrado. Verifique se o link está correto.", None
        elif error_code == 403:
            service_account_email = None
            try:
                from . import google_auth
                service_account_email = google_auth.get_service_account_email()
            except:
                pass
            
            error_msg = (
                "Acesso negado. O arquivo precisa ser compartilhado com o Service Account do sistema.\n\n"
                "Para resolver:\n"
                "1. Abra o arquivo no Google Drive\n"
                "2. Clique em 'Compartilhar' (botão no canto superior direito)\n"
            )
            
            if service_account_email:
                error_msg += f"3. Adicione o email: {service_account_email}\n"
                error_msg += "4. Defina a permissão como 'Visualizador'\n"
                error_msg += "5. Clique em 'Enviar'\n"
            else:
                error_msg += "3. Adicione o email do Service Account (consulte a documentação)\n"
                error_msg += "4. Defina a permissão como 'Visualizador'\n"
            
            return False, None, error_msg, None
        else:
            return False, None, f"Erro ao verificar acesso: {str(e)}", None
    except Exception as e:
        return False, None, f"Erro inesperado: {str(e)}", None


def download_file_from_drive(file_id: str, file_type: str) -> Tuple[bytes, str]:
    """
    Download a file from Google Drive.
    
    Args:
        file_id: Google Drive file ID
        file_type: Type of file ('google_sheets', 'excel', 'csv', 'tsv')
        
    Returns:
        Tuple of (file_content: bytes, filename: str)
        
    Raises:
        HttpError: If API call fails
        ValueError: If file_type is not supported
    """
    service = get_drive_service()
    
    if file_type == 'google_sheets':
        # Use Sheets API to export as Excel
        from . import sheets_service
        return sheets_service.fetch_sheet_as_excel_bytes(file_id), "planilha_google_sheets.xlsx"
    
    elif file_type in ['excel', 'csv', 'tsv']:
        # Download file directly using Drive API
        try:
            request = service.files().get_media(fileId=file_id)
            file_content = request.execute()
            
            # Get filename from metadata
            metadata = get_file_metadata(file_id)
            filename = metadata.get('name', f'arquivo.{file_type}')
            
            return file_content, filename
        except HttpError as e:
            raise ValueError(f"Erro ao baixar arquivo do Google Drive: {str(e)}")
    
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {file_type}")


def convert_to_google_sheets(file_id: str, file_type: str, original_name: str) -> Tuple[str, str]:
    """
    Converte um arquivo Excel, CSV ou TSV para Google Sheets nativo.
    
    Args:
        file_id: Google Drive file ID do arquivo original
        file_type: Tipo do arquivo ('excel', 'csv', 'tsv')
        original_name: Nome do arquivo original
        
    Returns:
        Tuple de (new_file_id: str, new_file_name: str) do Google Sheets criado
        
    Raises:
        HttpError: Se a API falhar
        ValueError: Se o tipo de arquivo não for suportado
    """
    if file_type not in ['excel', 'csv', 'tsv']:
        raise ValueError(f"Tipo de arquivo não pode ser convertido: {file_type}")
    
    service = get_drive_service()
    
    # Baixar o arquivo original
    file_content, filename = download_file_from_drive(file_id, file_type)
    
    # Criar um novo Google Sheets
    try:
        # Limpar nome do arquivo (remover extensões)
        clean_name = original_name
        for ext in ['.xlsx', '.xls', '.csv', '.tsv']:
            clean_name = clean_name.replace(ext, '')
        clean_name = clean_name.strip() + ' (Google Sheets)'
        
        # Criar arquivo Google Sheets vazio
        file_metadata = {
            'name': clean_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        
        created_file = service.files().create(
            body=file_metadata,
            fields='id,name,webViewLink'
        ).execute()
        
        new_file_id = created_file.get('id')
        new_file_name = created_file.get('name')
        
        # Importar os dados usando Sheets API
        try:
            from . import sheets_service
            sheets_service_obj = sheets_service.get_sheets_service()
            import pandas as pd
            
            # Ler o arquivo baixado
            if file_type == 'excel':
                df = pd.read_excel(io.BytesIO(file_content))
            elif file_type == 'csv':
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
            elif file_type == 'tsv':
                df = pd.read_csv(io.BytesIO(file_content), sep='\t', encoding='utf-8')
            
            # Converter DataFrame para lista de listas (formato do Sheets API)
            # Converter valores NaN para strings vazias
            df = df.fillna('')
            values = [df.columns.tolist()] + df.values.tolist()
            
            # Escrever dados no Google Sheets
            body = {
                'values': values
            }
            sheets_service_obj.spreadsheets().values().update(
                spreadsheetId=new_file_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()
        except Exception as e:
            # Se falhar ao importar dados, pelo menos o Google Sheets foi criado
            import logging
            logging.warning(f"Erro ao importar dados para Google Sheets: {str(e)}")
            # O Google Sheets vazio já foi criado, então retornamos mesmo assim
        
        return new_file_id, new_file_name
        
    except HttpError as e:
        error_code = e.resp.status if hasattr(e, 'resp') else None
        error_details = str(e)
        
        # Verificar se é erro de quota excedida
        if error_code == 403 and 'storageQuotaExceeded' in error_details:
            raise ValueError(
                "Cota de armazenamento do Google Drive excedida. "
                "O Service Account não tem mais espaço para criar novos arquivos. "
                "Soluções:\n"
                "1. Libere espaço no Google Drive do Service Account\n"
                "2. Ou use a aba 'Upload de Arquivo' para fazer upload direto (sem sincronização dinâmica)\n"
                "3. Ou converta manualmente o arquivo para Google Sheets e compartilhe"
            )
        raise ValueError(f"Erro ao criar Google Sheets: {str(e)}")
    except Exception as e:
        raise ValueError(f"Erro ao converter para Google Sheets: {str(e)}")
