"""
Webhook handler for Google Drive change notifications.
Handles dynamic synchronization of linked Google Sheets.
"""
import os
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, Header
from sqlalchemy.orm import Session
from . import models_sqlalchemy as models
from . import sheets_service
from . import drive_service
from . import google_drive_utils
from . import spreadsheet_ingestion


def verify_webhook_secret(request_body: bytes, x_goog_channel_token: Optional[str]) -> bool:
    """
    Verify webhook request authenticity using secret token.
    
    Args:
        request_body: Raw request body
        x_goog_channel_token: X-Goog-Channel-Token header value
        
    Returns:
        True if verified, False otherwise
    """
    expected_token = os.getenv('GOOGLE_WEBHOOK_SECRET')
    if not expected_token:
        return True
    
    if not x_goog_channel_token:
        return False
    
    return hmac.compare_digest(x_goog_channel_token, expected_token)


def sync_sheet_data(
    file_id: str,
    linked_sheet: models.LinkedSheet,
    db: Session
) -> Dict[str, Any]:
    """
    Synchronize spreadsheet data atomically.
    
    Process:
    1. Fetch latest spreadsheet data
    2. Validate all rows
    3. Update existing records or create new ones
    4. Log sync history
    5. Update last_sync timestamp
    
    Args:
        file_id: Google Sheets file ID
        linked_sheet: LinkedSheet database record
        db: Database session
        
    Returns:
        Dictionary with sync results
    """
    sync_start = datetime.utcnow()
    sync_history = models.SheetSyncHistory(
        linked_sheet_id=linked_sheet.id,
        sync_started_at=sync_start,
        status='processing'
    )
    db.add(sync_history)
    db.flush()
    
    try:
        file_content = sheets_service.fetch_sheet_as_excel_bytes(file_id)
        filename = f"sheet_{file_id}.xlsx"
        
        df, col_map, missing = spreadsheet_ingestion.ingest_spreadsheet(
            file_content,
            filename,
            'google_sheets'
        )
        
        imported = 0
        updated = 0
        skipped = 0
        errors = []
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                process_data = spreadsheet_ingestion.extract_row_data(row, col_map)
                
                processo_adm_1doc = process_data.get('processo_adm_1doc')
                processo_judicial = process_data.get('processo_judicial')
                
                if not processo_adm_1doc and not processo_judicial:
                    errors.append({
                        "row": idx + 2,
                        "message": "É obrigatório informar PROCESSO ADM 1DOC ou PROCESSO JUDICIAL"
                    })
                    error_count += 1
                    continue
                
                identifier = processo_adm_1doc or processo_judicial
                owner_id = linked_sheet.owner_user_id
                
                existing = None
                if processo_adm_1doc:
                    q = db.query(models.Process).filter(
                        models.Process.processo_adm_1doc == processo_adm_1doc
                    )
                    if owner_id is not None:
                        q = q.filter(models.Process.owner_user_id == owner_id)
                    existing = q.first()
                if not existing and processo_judicial:
                    q = db.query(models.Process).filter(
                        models.Process.processo_judicial == processo_judicial
                    )
                    if owner_id is not None:
                        q = q.filter(models.Process.owner_user_id == owner_id)
                    existing = q.first()
                
                if existing:
                    # Coletar campos atualizados para auditoria
                    updated_fields = {}
                    
                    new_partes = process_data.get('partes')
                    if new_partes and new_partes != existing.partes:
                        updated_fields['partes'] = new_partes
                        existing.partes = new_partes
                    
                    new_tema = process_data.get('tema_observacoes')
                    if new_tema and new_tema != existing.tema_observacoes:
                        updated_fields['tema_observacoes'] = new_tema
                        existing.tema_observacoes = new_tema
                    
                    new_data_receb = process_data.get('data_recebimento_mes_ano')
                    if new_data_receb and new_data_receb != existing.data_recebimento_mes_ano:
                        updated_fields['data_recebimento_mes_ano'] = new_data_receb
                        existing.data_recebimento_mes_ano = new_data_receb
                    
                    new_prazo_info = process_data.get('prazo_info_estag')
                    if new_prazo_info and new_prazo_info != existing.prazo_info_estag:
                        updated_fields['prazo_info_estag'] = new_prazo_info
                        existing.prazo_info_estag = new_prazo_info
                    
                    new_prazo_final = process_data.get('prazo_final')
                    if new_prazo_final and new_prazo_final != existing.prazo_final:
                        updated_fields['prazo_final'] = new_prazo_final
                        existing.prazo_final = new_prazo_final
                    
                    new_tipo_ato = process_data.get('tipo_ato')
                    if new_tipo_ato and new_tipo_ato != existing.tipo_ato:
                        updated_fields['tipo_ato'] = new_tipo_ato
                        existing.tipo_ato = new_tipo_ato
                    
                    new_data_ato = process_data.get('data_realizacao_ato')
                    if new_data_ato and new_data_ato != existing.data_realizacao_ato:
                        updated_fields['data_realizacao_ato'] = new_data_ato
                        existing.data_realizacao_ato = new_data_ato
                    
                    if updated_fields:
                        # Registrar mudanças no histórico de auditoria
                        from backend import audit_service
                        audit_service.AuditService.record_process_update(
                            db=db,
                            process=existing,
                            updated_fields=updated_fields,
                            change_source='google_sheets',
                            source_details={
                                'file_id': file_id,
                                'linked_sheet_id': linked_sheet.id,
                                'sync_type': 'webhook',
                                'sync_history_id': sync_history.id
                            }
                        )
                    
                    updated += 1
                else:
                    new_process = models.Process(
                        processo_adm_1doc=processo_adm_1doc,
                        processo_judicial=processo_judicial,
                        partes=process_data.get('partes'),
                        tema_observacoes=process_data.get('tema_observacoes'),
                        data_recebimento_mes_ano=process_data.get('data_recebimento_mes_ano'),
                        prazo_info_estag=process_data.get('prazo_info_estag'),
                        prazo_final=process_data.get('prazo_final'),
                        tipo_ato=process_data.get('tipo_ato'),
                        data_realizacao_ato=process_data.get('data_realizacao_ato'),
                        applicant_registration=process_data.get('applicant_registration'),
                        notes=process_data.get('notes'),
                        protocol_number=identifier,
                        created_date=datetime.utcnow().date(),
                        owner_user_id=owner_id,
                    )
                    db.add(new_process)
                    db.flush()
                    
                    # Registrar criação no histórico de auditoria
                    from backend import audit_service
                    audit_service.AuditService.record_process_creation(
                        db=db,
                        process_id=new_process.id,
                        process_data=process_data,
                        change_source='google_sheets',
                        source_details={
                            'file_id': file_id,
                            'linked_sheet_id': linked_sheet.id,
                            'sync_type': 'webhook',
                            'sync_history_id': sync_history.id
                        }
                    )
                    
                    imported += 1
                
            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "message": str(e)
                })
                error_count += 1
        
        sync_end = datetime.utcnow()
        
        linked_sheet.last_sync = sync_end
        sync_history.sync_completed_at = sync_end
        sync_history.status = 'success' if error_count == 0 else 'error'
        sync_history.rows_processed = len(df)
        sync_history.rows_imported = imported
        sync_history.rows_updated = updated
        sync_history.rows_skipped = skipped
        sync_history.errors_count = error_count
        sync_history.error_message = None if error_count == 0 else f"{error_count} erro(s) encontrado(s)"
        sync_history.sync_details = json.dumps({
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "errors": errors[:10],
            "total_errors": error_count
        }, ensure_ascii=False)
        
        db.commit()
        
        return {
            "status": "success",
            "file_id": file_id,
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "errors": errors[:10],
            "total_errors": error_count,
            "sync_history_id": sync_history.id,
            "sync_duration_seconds": (sync_end - sync_start).total_seconds()
        }
        
    except ValueError as e:
        sync_end = datetime.utcnow()
        sync_history.sync_completed_at = sync_end
        sync_history.status = 'error'
        sync_history.error_message = str(e)
        db.commit()
        
        return {
            "status": "error",
            "message": str(e),
            "file_id": file_id,
            "sync_history_id": sync_history.id
        }
    except Exception as e:
        sync_end = datetime.utcnow()
        sync_history.sync_completed_at = sync_end
        sync_history.status = 'error'
        sync_history.error_message = str(e)
        db.rollback()
        
        return {
            "status": "error",
            "message": f"Erro ao processar planilha: {str(e)}",
            "file_id": file_id,
            "sync_history_id": sync_history.id
        }


async def handle_drive_webhook(
    request: Request,
    x_goog_channel_id: str = Header(..., alias='X-Goog-Channel-Id'),
    x_goog_channel_token: Optional[str] = Header(None, alias='X-Goog-Channel-Token'),
    x_goog_resource_id: str = Header(..., alias='X-Goog-Resource-Id'),
    x_goog_resource_state: str = Header(..., alias='X-Goog-Resource-State'),
    x_goog_resource_uri: Optional[str] = Header(None, alias='X-Goog-Resource-Uri'),
    x_goog_changed: Optional[str] = Header(None, alias='X-Goog-Changed')
) -> Dict[str, Any]:
    """
    Handle Google Drive webhook notification.
    
    On change event:
    - Re-fetches spreadsheet
    - Re-runs validation
    - Updates records atomically
    - Logs sync history
    - Updates last_synced_at
    
    Args:
        request: FastAPI request object
        x_goog_channel_id: Channel ID
        x_goog_channel_token: Optional secret token
        x_goog_resource_id: Resource ID
        x_goog_resource_state: State (sync, update, etc)
        x_goog_resource_uri: Resource URI
        x_goog_changed: What changed
        
    Returns:
        Response dictionary
        
    Raises:
        HTTPException: If verification fails or processing error
    """
    body = await request.body()
    
    if not verify_webhook_secret(body, x_goog_channel_token):
        raise HTTPException(status_code=403, detail="Invalid webhook token")
    
    if x_goog_resource_state not in ('update', 'sync'):
        return {
            "status": "ignored",
            "reason": f"State {x_goog_resource_state} not processed",
            "resource_id": x_goog_resource_id
        }
    
    engine = models.get_engine()
    db = models.get_session(engine)
    
    try:
        linked_sheet = db.query(models.LinkedSheet).filter(
            models.LinkedSheet.resource_id == x_goog_resource_id,
            models.LinkedSheet.is_active == True
        ).first()
        
        if not linked_sheet:
            return {
                "status": "not_found",
                "resource_id": x_goog_resource_id,
                "message": "Linked sheet not found or inactive"
            }
        
        file_id = linked_sheet.file_id
        
        result = sync_sheet_data(file_id, linked_sheet, db)
        return result
        
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"Erro ao processar webhook: {str(e)}",
            "resource_id": x_goog_resource_id
        }
    finally:
        db.close()
