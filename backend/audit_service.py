"""
Audit service for tracking process changes.
Provides legal audit trail and traceability.
"""
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from . import models_sqlalchemy as models


# Mapeamento de campos para labels legíveis
FIELD_LABELS = {
    'processo_adm_1doc': 'PROCESSO ADM 1DOC',
    'processo_judicial': 'PROCESSO JUDICIAL',
    'partes': 'PARTES',
    'tema_observacoes': 'TEMA – OBSERVAÇÕES',
    'data_recebimento_mes_ano': 'DATA RECEBIMENTO (MÊS/ANO)',
    'prazo_info_estag': 'PRAZO INFO – ESTAG (DIA/MÊS)',
    'prazo_final': 'PRAZO FINAL (DD/MM)',
    'tipo_ato': 'TIPO DE ATO',
    'data_realizacao_ato': 'DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)',
    'protocol_number': 'Número de Protocolo',
    'applicant_name': 'Nome do Requerente',
    'applicant_registration': 'Matrícula',
    'created_date': 'Data de Criação',
    'notes': 'Observações',
    'parecer': 'Parecer',
    'financial_effective_date': 'Data de Efeito Financeiro',
    'closed_date': 'Data de Fechamento',
}


class AuditService:
    """
    Service for creating audit trail records.
    """
    
    @staticmethod
    def _serialize_value(value: Any) -> Optional[str]:
        """Serialize value for storage."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return str(value)
    
    @staticmethod
    def get_field_label(field_name: str) -> str:
        """Get human-readable label for field."""
        return FIELD_LABELS.get(field_name, field_name.replace('_', ' ').title())
    
    @staticmethod
    def _get_field_label(field_name: str) -> str:
        """Get human-readable label for field (internal alias)."""
        return AuditService.get_field_label(field_name)
    
    @staticmethod
    def record_change(
        db: Session,
        process_id: int,
        field_name: str,
        old_value: Any,
        new_value: Any,
        change_source: str,
        source_details: Optional[Dict] = None,
        changed_by_user_id: Optional[int] = None,
        change_type: str = 'update'
    ) -> models.ProcessChangeHistory:
        """
        Record a single field change in the audit trail.
        
        Args:
            db: Database session
            process_id: Process ID
            field_name: Name of the changed field
            old_value: Previous value
            new_value: New value
            change_source: Source of change ('upload', 'google_sheets', 'manual', 'api')
            source_details: Optional dictionary with additional source information
            changed_by_user_id: ID of user who made the change (if applicable)
            change_type: Type of change ('create', 'update', 'delete')
            
        Returns:
            Created ProcessChangeHistory record
        """
        # Get process for identification
        process = db.query(models.Process).filter(
            models.Process.id == process_id
        ).first()
        
        if not process:
            raise ValueError(f"Process {process_id} not found")
        
        # Serialize values
        old_val_str = AuditService._serialize_value(old_value)
        new_val_str = AuditService._serialize_value(new_value)
        
        # Skip if values are the same
        if old_val_str == new_val_str:
            return None
        
        # Create change history record
        change_record = models.ProcessChangeHistory(
            process_id=process_id,
            processo_adm_1doc=process.processo_adm_1doc,
            processo_judicial=process.processo_judicial,
            protocol_number=process.protocol_number,
            field_name=field_name,
            field_label=AuditService._get_field_label(field_name),
            old_value=old_val_str,
            new_value=new_val_str,
            change_source=change_source,
            source_details=json.dumps(source_details, ensure_ascii=False) if source_details else None,
            changed_by_user_id=changed_by_user_id,
            change_type=change_type,
            changed_at=datetime.utcnow()
        )
        
        db.add(change_record)
        return change_record
    
    @staticmethod
    def record_process_creation(
        db: Session,
        process_id: int,
        process_data: Dict,
        change_source: str,
        source_details: Optional[Dict] = None,
        changed_by_user_id: Optional[int] = None
    ) -> List[models.ProcessChangeHistory]:
        """
        Record creation of a new process.
        
        Creates change history records for all initial field values.
        
        Args:
            db: Database session
            process_id: Process ID
            process_data: Dictionary with initial process data
            change_source: Source of creation
            source_details: Optional source details
            changed_by_user_id: ID of user who created (if applicable)
            
        Returns:
            List of created change history records
        """
        records = []
        
        for field_name, value in process_data.items():
            if field_name in FIELD_LABELS:
                record = AuditService.record_change(
                    db=db,
                    process_id=process_id,
                    field_name=field_name,
                    old_value=None,
                    new_value=value,
                    change_source=change_source,
                    source_details=source_details,
                    changed_by_user_id=changed_by_user_id,
                    change_type='create'
                )
                if record:
                    records.append(record)
        
        return records
    
    @staticmethod
    def record_process_update(
        db: Session,
        process: models.Process,
        updated_fields: Dict,
        change_source: str,
        source_details: Optional[Dict] = None,
        changed_by_user_id: Optional[int] = None
    ) -> List[models.ProcessChangeHistory]:
        """
        Record updates to a process.
        
        Compares current values with new values and records only changed fields.
        
        Args:
            db: Database session
            process: Process model instance
            updated_fields: Dictionary with field_name -> new_value
            change_source: Source of update
            source_details: Optional source details
            changed_by_user_id: ID of user who updated (if applicable)
            
        Returns:
            List of created change history records
        """
        records = []
        
        for field_name, new_value in updated_fields.items():
            if field_name in FIELD_LABELS:
                old_value = getattr(process, field_name, None)
                
                record = AuditService.record_change(
                    db=db,
                    process_id=process.id,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    change_source=change_source,
                    source_details=source_details,
                    changed_by_user_id=changed_by_user_id,
                    change_type='update'
                )
                if record:
                    records.append(record)
        
        return records
    
    @staticmethod
    def get_process_history(
        db: Session,
        process_id: int,
        field_name: Optional[str] = None,
        change_source: Optional[str] = None,
        limit: int = 100
    ) -> List[models.ProcessChangeHistory]:
        """
        Get change history for a process.
        
        Args:
            db: Database session
            process_id: Process ID
            field_name: Optional filter by field name
            change_source: Optional filter by change source
            limit: Maximum number of records to return
            
        Returns:
            List of change history records, ordered by most recent first
        """
        query = db.query(models.ProcessChangeHistory).filter(
            models.ProcessChangeHistory.process_id == process_id
        )
        
        if field_name:
            query = query.filter(models.ProcessChangeHistory.field_name == field_name)
        
        if change_source:
            query = query.filter(models.ProcessChangeHistory.change_source == change_source)
        
        return query.order_by(
            models.ProcessChangeHistory.changed_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_field_history(
        db: Session,
        process_id: int,
        field_name: str,
        limit: int = 50
    ) -> List[models.ProcessChangeHistory]:
        """
        Get history for a specific field of a process.
        
        Args:
            db: Database session
            process_id: Process ID
            field_name: Field name
            limit: Maximum number of records
            
        Returns:
            List of change history records for the field
        """
        return AuditService.get_process_history(
            db=db,
            process_id=process_id,
            field_name=field_name,
            limit=limit
        )
