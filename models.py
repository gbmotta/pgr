"""
Modelos de dados (dataclasses Python) para referência e validação.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List

@dataclass
class ProcessType:
    id: Optional[int]
    code: str
    name: str
    description: Optional[str] = None

@dataclass
class Status:
    id: Optional[int]
    code: str
    label: str

@dataclass
class Document:
    id: Optional[int]
    code: str
    name: str
    description: Optional[str] = None

@dataclass
class RequiredDocument:
    id: Optional[int]
    type_id: int
    document_id: int
    required: bool = True
    doc_order: int = 0

@dataclass
class ProcessDocument:
    id: Optional[int]
    process_id: int
    document_id: int
    required: bool = True
    provided: bool = False
    provided_date: Optional[date] = None
    observations: Optional[str] = None

@dataclass
class LegalDeadline:
    id: Optional[int]
    type_id: Optional[int]
    name: str
    days_limit: int
    start_event: str
    is_business_days: bool = False
    description: Optional[str] = None

@dataclass
class ProcessDeadline:
    id: Optional[int]
    process_id: int
    legal_deadline_id: int
    due_date: date
    notified: bool = False
    closed: bool = False
    notes: Optional[str] = None

@dataclass
class Process:
    id: Optional[int]
    protocol_number: str
    type_id: int
    applicant_name: str
    applicant_registration: Optional[str]
    created_date: date
    status_id: int
    parecer: Optional[str] = None
    financial_effective_date: Optional[date] = None
    closed_date: Optional[date] = None
    notes: Optional[str] = None
    documents: List[ProcessDocument] = field(default_factory=list)
    deadlines: List[ProcessDeadline] = field(default_factory=list)
