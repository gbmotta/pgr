"""
API REST com SQLAlchemy - Sistema de Processos Administrativos
Endpoints comentados e organizados para fácil manutenção.
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta
import models_sqlalchemy as models

# ============ Configuração da Aplicação ============

app = FastAPI(
    title="PGR - Sistema de Processos (SQLAlchemy)",
    description="API REST para controle de processos administrativos com ORM",
    version="2.0.0"
)

# Inicializar banco de dados na primeira execução
engine = models.get_engine()
models.create_tables(engine)

# Servir arquivos estáticos (frontend)
app.mount("/pgr", StaticFiles(directory="pgr", html=True), name="pgr")


# ============ Schemas Pydantic (DTOs) ============

class ProcessCreateSchema(BaseModel):
    """
    Schema para criação de novo processo.
    Validação de dados de entrada via Pydantic.
    """
    protocol_number: str  # Número de protocolo único (ex: PGR-2025-0001)
    type_code: str  # Código do tipo (PROM_CAP ou PROG_MER)
    applicant_name: str  # Nome completo do requerente
    applicant_registration: Optional[str] = None  # Matrícula do servidor (opcional)
    created_date: Optional[str] = None  # Data de criação (YYYY-MM-DD, default: hoje)
    status_code: str = "RECEBIDO"  # Status inicial (default: RECEBIDO)
    notes: Optional[str] = None  # Observações iniciais (opcional)


class ProcessResponseSchema(BaseModel):
    """
    Schema de resposta com dados básicos do processo.
    """
    id: int
    protocol_number: str
    type_code: str
    applicant_name: str
    created_date: str
    status_code: str
    financial_effective_date: Optional[str]
    
    class Config:
        from_attributes = True  # Permite conversão de modelo SQLAlchemy


class DeadlineResponseSchema(BaseModel):
    """
    Schema de resposta para prazos vencidos.
    """
    protocol_number: str
    type_name: str
    deadline_name: str
    due_date: str
    days_overdue: int
    notified: bool


# ============ Dependency Injection ============

def get_db():
    """
    Fornece uma sessão de banco de dados para cada requisição.
    Garante que a sessão seja fechada corretamente.
    """
    db = models.get_session(engine)
    try:
        yield db  # Injeta a sessão no endpoint
    finally:
        db.close()  # Fecha a sessão após a requisição


# ============ Funções Auxiliares ============

def calculate_due_date(start_date: date, days: int, business_days: bool = False) -> date:
    """
    Calcula data de vencimento a partir de uma data inicial.
    
    Args:
        start_date: Data inicial
        days: Quantidade de dias a adicionar
        business_days: Se True, conta apenas dias úteis (seg-sex)
    
    Returns:
        Data de vencimento calculada
    """
    if not business_days:
        # Dias corridos: apenas adiciona
        return start_date + timedelta(days=days)
    
    # Dias úteis: pula fins de semana
    current = start_date
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # 0=Segunda, 4=Sexta
            added += 1
    return current


def create_process_checklist(db: Session, process_id: int, type_id: int):
    """
    Cria checklist de documentos para um processo baseado no tipo.
    
    Args:
        db: Sessão do banco
        process_id: ID do processo
        type_id: ID do tipo de processo
    """
    # Buscar documentos obrigatórios para este tipo
    required_docs = db.query(models.RequiredDocument).filter(
        models.RequiredDocument.type_id == type_id
    ).all()
    
    # Criar entrada no checklist para cada documento
    for req_doc in required_docs:
        proc_doc = models.ProcessDocument(
            process_id=process_id,
            document_id=req_doc.document_id,
            required=req_doc.required,
            provided=False  # Inicialmente não fornecido
        )
        db.add(proc_doc)
    
    db.commit()


def create_process_deadlines(db: Session, process_id: int, type_id: int, created_date: date):
    """
    Cria prazos para um processo baseado nos prazos legais.
    
    Args:
        db: Sessão do banco
        process_id: ID do processo
        type_id: ID do tipo de processo
        created_date: Data de criação do processo
    """
    # Buscar prazos legais aplicáveis (específicos do tipo ou gerais)
    legal_deadlines = db.query(models.LegalDeadline).filter(
        (models.LegalDeadline.type_id == type_id) | 
        (models.LegalDeadline.type_id == None)
    ).all()
    
    for legal_dl in legal_deadlines:
        # Por enquanto, suporta apenas start_event='created_date'
        if legal_dl.start_event == 'created_date':
            # Calcular data de vencimento
            due = calculate_due_date(
                created_date,
                legal_dl.days_limit,
                legal_dl.is_business_days
            )
            
            # Criar prazo para o processo
            proc_deadline = models.ProcessDeadline(
                process_id=process_id,
                legal_deadline_id=legal_dl.id,
                due_date=due,
                notified=False,
                closed=False
            )
            db.add(proc_deadline)
    
    db.commit()


# ============ Endpoints da API ============

@app.get("/")
def root():
    """
    Endpoint raiz - informações da API.
    """
    return {
        "message": "PGR API - Sistema de Processos Administrativos",
        "version": "2.0.0",
        "orm": "SQLAlchemy",
        "docs": "/docs"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Verifica se a API e o banco de dados estão funcionando.
    """
    try:
        # Tenta fazer uma query simples
        db.query(models.ProcessType).first()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


@app.post("/processes", status_code=201, response_model=ProcessResponseSchema)
def create_process(payload: ProcessCreateSchema, db: Session = Depends(get_db)):
    """
    Cadastra um novo processo administrativo.
    
    Fluxo:
    1. Valida tipo de processo e status
    2. Cria registro do processo
    3. Gera checklist de documentos automaticamente
    4. Calcula e cria prazos legais
    
    Args:
        payload: Dados do processo a ser criado
        db: Sessão do banco (injetada)
    
    Returns:
        Dados do processo criado
    
    Raises:
        HTTPException 400: Dados inválidos
        HTTPException 409: Protocolo já existe
    """
    # 1. Validar tipo de processo
    process_type = db.query(models.ProcessType).filter(
        models.ProcessType.code == payload.type_code
    ).first()
    
    if not process_type:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de processo inválido: {payload.type_code}"
        )
    
    # 2. Validar status
    status = db.query(models.Status).filter(
        models.Status.code == payload.status_code
    ).first()
    
    if not status:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido: {payload.status_code}"
        )
    
    # 3. Verificar se protocolo já existe
    existing = db.query(models.Process).filter(
        models.Process.protocol_number == payload.protocol_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Protocolo já existe: {payload.protocol_number}"
        )
    
    # 4. Definir data de criação (hoje se não informada)
    created_date = date.fromisoformat(payload.created_date) if payload.created_date else date.today()
    
    # 5. Criar o processo
    new_process = models.Process(
        protocol_number=payload.protocol_number,
        type_id=process_type.id,
        applicant_name=payload.applicant_name,
        applicant_registration=payload.applicant_registration,
        created_date=created_date,
        status_id=status.id,
        notes=payload.notes
    )
    
    db.add(new_process)
    db.commit()
    db.refresh(new_process)  # Atualiza com o ID gerado
    
    # 6. Gerar checklist de documentos
    create_process_checklist(db, new_process.id, process_type.id)
    
    # 7. Gerar prazos legais
    create_process_deadlines(db, new_process.id, process_type.id, created_date)
    
    # 8. Retornar resposta
    return ProcessResponseSchema(
        id=new_process.id,
        protocol_number=new_process.protocol_number,
        type_code=process_type.code,
        applicant_name=new_process.applicant_name,
        created_date=str(new_process.created_date),
        status_code=status.code,
        financial_effective_date=str(new_process.financial_effective_date) if new_process.financial_effective_date else None
    )


@app.get("/processes", response_model=List[ProcessResponseSchema])
def list_processes(
    type_code: Optional[str] = Query(None, description="Filtrar por tipo de processo"),
    status_code: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os processos com filtros opcionais.
    
    Args:
        type_code: Código do tipo para filtrar (opcional)
        status_code: Código do status para filtrar (opcional)
        db: Sessão do banco (injetada)
    
    Returns:
        Lista de processos
    """
    # Query base com joins
    query = db.query(models.Process).join(models.ProcessType).join(models.Status)
    
    # Aplicar filtros se fornecidos
    if type_code:
        query = query.filter(models.ProcessType.code == type_code)
    
    if status_code:
        query = query.filter(models.Status.code == status_code)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(models.Process.created_date.desc())
    
    # Executar query
    processes = query.all()
    
    # Converter para schema de resposta
    result = []
    for proc in processes:
        result.append(ProcessResponseSchema(
            id=proc.id,
            protocol_number=proc.protocol_number,
            type_code=proc.process_type.code,
            applicant_name=proc.applicant_name,
            created_date=str(proc.created_date),
            status_code=proc.status.code,
            financial_effective_date=str(proc.financial_effective_date) if proc.financial_effective_date else None
        ))
    
    return result


@app.get("/processes/{protocol}")
def get_process_details(protocol: str, db: Session = Depends(get_db)):
    """
    Busca detalhes completos de um processo incluindo checklist e prazos.
    
    Args:
        protocol: Número do protocolo
        db: Sessão do banco (injetada)
    
    Returns:
        Detalhes completos do processo
    
    Raises:
        HTTPException 404: Processo não encontrado
    """
    # Buscar processo com relacionamentos
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(
            status_code=404,
            detail=f"Processo não encontrado: {protocol}"
        )
    
    # Montar resposta completa
    return {
        "id": process.id,
        "protocol_number": process.protocol_number,
        "type": {
            "code": process.process_type.code,
            "name": process.process_type.name
        },
        "applicant_name": process.applicant_name,
        "applicant_registration": process.applicant_registration,
        "created_date": str(process.created_date),
        "status": {
            "code": process.status.code,
            "label": process.status.label
        },
        "parecer": process.parecer,
        "financial_effective_date": str(process.financial_effective_date) if process.financial_effective_date else None,
        "closed_date": str(process.closed_date) if process.closed_date else None,
        "notes": process.notes,
        "documents": [
            {
                "code": doc.document.code,
                "name": doc.document.name,
                "required": doc.required,
                "provided": doc.provided,
                "provided_date": str(doc.provided_date) if doc.provided_date else None,
                "observations": doc.observations
            }
            for doc in process.documents
        ],
        "deadlines": [
            {
                "name": dl.legal_deadline.name,
                "due_date": str(dl.due_date),
                "days_limit": dl.legal_deadline.days_limit,
                "notified": dl.notified,
                "closed": dl.closed,
                "notes": dl.notes
            }
            for dl in process.deadlines
        ]
    }


@app.get("/deadlines/overdue", response_model=List[DeadlineResponseSchema])
def list_overdue_deadlines(db: Session = Depends(get_db)):
    """
    Lista todos os prazos vencidos (não fechados).
    
    Critérios:
    - due_date < hoje
    - closed = False
    
    Args:
        db: Sessão do banco (injetada)
    
    Returns:
        Lista de prazos vencidos com dias de atraso
    """
    today = date.today()
    
    # Query com joins para pegar informações relacionadas
    overdue = db.query(models.ProcessDeadline).join(
        models.Process
    ).join(
        models.ProcessType
    ).join(
        models.LegalDeadline
    ).filter(
        models.ProcessDeadline.closed == False,  # Apenas não fechados
        models.ProcessDeadline.due_date < today  # Vencidos
    ).order_by(
        models.ProcessDeadline.due_date.asc()  # Mais antigos primeiro
    ).all()
    
    # Montar resposta com cálculo de dias de atraso
    result = []
    for deadline in overdue:
        days_overdue = (today - deadline.due_date).days
        
        result.append(DeadlineResponseSchema(
            protocol_number=deadline.process.protocol_number,
            type_name=deadline.process.process_type.name,
            deadline_name=deadline.legal_deadline.name,
            due_date=str(deadline.due_date),
            days_overdue=days_overdue,
            notified=deadline.notified
        ))
    
    return result


@app.get("/deadlines/upcoming")
def list_upcoming_deadlines(
    days: int = Query(7, ge=1, le=90, description="Quantidade de dias à frente"),
    db: Session = Depends(get_db)
):
    """
    Lista prazos próximos do vencimento.
    
    Args:
        days: Quantidade de dias à frente para buscar (default: 7)
        db: Sessão do banco (injetada)
    
    Returns:
        Lista de prazos próximos
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    
    # Query prazos no intervalo
    upcoming = db.query(models.ProcessDeadline).join(
        models.Process
    ).join(
        models.ProcessType
    ).join(
        models.LegalDeadline
    ).filter(
        models.ProcessDeadline.closed == False,
        models.ProcessDeadline.due_date >= today,
        models.ProcessDeadline.due_date <= end_date
    ).order_by(
        models.ProcessDeadline.due_date.asc()
    ).all()
    
    # Montar resposta
    result = []
    for deadline in upcoming:
        days_remaining = (deadline.due_date - today).days
        
        result.append({
            "protocol_number": deadline.process.protocol_number,
            "type_name": deadline.process.process_type.name,
            "deadline_name": deadline.legal_deadline.name,
            "due_date": str(deadline.due_date),
            "days_remaining": days_remaining,
            "notified": deadline.notified
        })
    
    return result


@app.get("/statistics/summary")
def get_statistics(db: Session = Depends(get_db)):
    """
    Retorna estatísticas gerais do sistema.
    
    Returns:
        Resumo com contadores
    """
    total_processes = db.query(models.Process).count()
    
    # Contar por status
    by_status = {}
    statuses = db.query(models.Status).all()
    for status in statuses:
        count = db.query(models.Process).filter(
            models.Process.status_id == status.id
        ).count()
        by_status[status.code] = count
    
    # Contar prazos vencidos
    today = date.today()
    overdue_count = db.query(models.ProcessDeadline).filter(
        models.ProcessDeadline.closed == False,
        models.ProcessDeadline.due_date < today
    ).count()
    
    return {
        "total_processes": total_processes,
        "by_status": by_status,
        "overdue_deadlines": overdue_count,
        "generated_at": str(date.today())
    }


# ============ Script de Inicialização ============

if __name__ == "__main__":
    """
    Executa a API com uvicorn quando chamado diretamente.
    """
    import uvicorn
    uvicorn.run(
        "api_sqlalchemy:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload em desenvolvimento
    )
