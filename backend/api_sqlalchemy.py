"""
API REST com SQLAlchemy - Sistema de Processos Administrativos PGR

Este módulo implementa a API REST principal do sistema de controle de processos
administrativos de Promoção por Capacitação Profissional (PROM_CAP) e 
Progressão por Mérito Profissional (PROG_MER).

Funcionalidades principais:
- CRUD completo de processos
- Checklist automático de documentos por tipo de processo
- Cálculo automático de prazos legais
- Consulta de processos por protocolo, tipo e status
- Estatísticas e relatórios
- API endpoints para frontend

Tecnologias:
- FastAPI: Framework web assíncrono
- SQLAlchemy: ORM para banco de dados
- Pydantic: Validação de dados
- SQLite: Banco de dados

Autor: Sistema PGR
Versão: 2.0.0
Data: Dezembro 2025
"""
from fastapi import FastAPI, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta, datetime
from pathlib import Path
import os

# Importar models - funciona tanto como módulo quanto como pacote
try:
    # Quando executado como pacote: python -m backend.api_sqlalchemy
    from . import models_sqlalchemy as models
except ImportError:
    # Quando executado diretamente: uvicorn backend.api_sqlalchemy:app
    import models_sqlalchemy as models

# ============ Configuração da Aplicação ============

app = FastAPI(
    title="PGR - Sistema de Processos (SQLAlchemy)",
    description="API REST para controle de processos administrativos com ORM",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados na primeira execução
# O banco ficará em data/PGR.db
engine = models.get_engine()
models.create_tables(engine)

# Servir arquivos estáticos (frontend React será servido aqui)
# Uploads também
uploads_path = Path(__file__).parent.parent / "uploads"
uploads_path.mkdir(exist_ok=True)

# Em produção, o React será buildado e servido aqui
frontend_dist_path = Path(__file__).parent.parent / "frontend-dist"
frontend_old_path = Path(__file__).parent.parent / "frontend"

# Servir assets estáticos do React
if frontend_dist_path.exists() and (frontend_dist_path / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")

# Fallback para frontend antigo
if frontend_old_path.exists():
    app.mount("/pgr", StaticFiles(directory=str(frontend_old_path), html=True), name="pgr")

# Importar utilitários e auth
try:
    from . import auth
    from . import utils
except ImportError:
    import auth
    import utils


# ============ Schemas Pydantic (DTOs) ============
# Schemas definem a estrutura de dados para requisições e respostas

# ============ Schemas de Autenticação ============

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    
    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user: UserResponseSchema


# ============ Schemas de Processos ============

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
        (models.LegalDeadline.type_id.is_(None))
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


@app.delete("/processes/{protocol}")
def delete_process(protocol: str, db: Session = Depends(get_db)):
    """
    Deleta um processo pelo número do protocolo.
    
    Args:
        protocol: Número do protocolo
        db: Sessão do banco (injetada)
    
    Returns:
        Mensagem de confirmação
    
    Raises:
        HTTPException 404: Processo não encontrado
    """
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(
            status_code=404,
            detail=f"Processo não encontrado: {protocol}"
        )
    
    db.delete(process)
    db.commit()
    
    return {
        "message": f"Processo {protocol} deletado com sucesso",
        "protocol": protocol
    }


@app.post("/processes/bulk-delete")
def bulk_delete_processes(
    protocols: List[str],
    db: Session = Depends(get_db)
):
    """
    Deleta múltiplos processos em lote.
    
    Args:
        protocols: Lista de números de protocolo
        db: Sessão do banco (injetada)
    
    Returns:
        Estatísticas da operação
    """
    deleted = 0
    not_found = []
    
    for protocol in protocols:
        process = db.query(models.Process).filter(
            models.Process.protocol_number == protocol
        ).first()
        
        if process:
            db.delete(process)
            deleted += 1
        else:
            not_found.append(protocol)
    
    db.commit()
    
    return {
        "message": f"{deleted} processo(s) deletado(s)",
        "deleted": deleted,
        "not_found": not_found,
        "total_requested": len(protocols)
    }


@app.post("/processes/bulk-delete-pattern")
def bulk_delete_by_pattern(
    pattern: str = Query(..., description="Padrão do protocolo (ex: PGR-2025-08%)"),
    db: Session = Depends(get_db)
):
    """
    Deleta processos que correspondem a um padrão SQL LIKE.
    
    Args:
        pattern: Padrão SQL LIKE (ex: 'PGR-2025-08%' deleta todos os 0800-0899)
        db: Sessão do banco (injetada)
    
    Returns:
        Estatísticas da operação
    
    Examples:
        - PGR-2025-08%: Deleta todos os processos 0800-0899
        - PGR-2025-%: Deleta todos os processos de 2025
        - %TEST%: Deleta processos com TEST no protocolo
    """
    # Buscar processos que correspondem ao padrão
    processes = db.query(models.Process).filter(
        models.Process.protocol_number.like(pattern)
    ).all()
    
    if not processes:
        return {
            "message": "Nenhum processo encontrado com esse padrão",
            "deleted": 0,
            "pattern": pattern
        }
    
    # Coletar protocolos antes de deletar
    deleted_protocols = [p.protocol_number for p in processes]
    
    # Deletar todos
    db.query(models.Process).filter(
        models.Process.protocol_number.like(pattern)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"{len(deleted_protocols)} processo(s) deletado(s)",
        "deleted": len(deleted_protocols),
        "pattern": pattern,
        "protocols": deleted_protocols[:20]  # Mostrar no máximo 20
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
        models.ProcessDeadline.closed.is_(False),  # Apenas não fechados
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
        models.ProcessDeadline.closed.is_(False),
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
        models.ProcessDeadline.closed.is_(False),
        models.ProcessDeadline.due_date < today
    ).count()
    
    return {
        "total_processes": total_processes,
        "by_status": by_status,
        "overdue_deadlines": overdue_count,
        "generated_at": str(date.today())
    }


# ============ Endpoints de Autenticação ============

@app.post("/api/auth/register", response_model=UserResponseSchema)
def register(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    """Registra novo usuário."""
    # Verificar se username já existe
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | 
        (models.User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username ou email já existe"
        )
    
    # Criar usuário
    hashed_password = auth.get_password_hash(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post("/api/auth/login", response_model=TokenSchema)
def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    """Autentica usuário e retorna token JWT."""
    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()
    
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Usuário inativo"
        )
    
    # Gerar token
    access_token = auth.create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponseSchema.from_orm(user)
    }


@app.get("/api/auth/me", response_model=UserResponseSchema)
def get_current_user_info(current_user = Depends(auth.get_current_active_user)):
    """Retorna informações do usuário logado."""
    return current_user


# ============ Endpoints de Upload ============

@app.post("/processes/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Upload e importação de processos via planilha Excel."""
    import pandas as pd
    import io
    
    # Ler arquivo
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    
    # Normalizar nomes das colunas
    df.columns = df.columns.str.strip().str.lower()
    
    # Mapear colunas
    col_map = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if "protocolo" in col_lower or "numero" in col_lower or "processo" in col_lower:
            col_map["protocol_number"] = col
        elif "tipo" in col_lower:
            col_map["type_code"] = col
        elif "requerente" in col_lower or ("nome" in col_lower and "servidor" in col_lower):
            col_map["applicant_name"] = col
        elif "matricula" in col_lower or "matrícula" in col_lower:
            col_map["applicant_registration"] = col
        elif "data" in col_lower and ("criação" in col_lower or "abertura" in col_lower):
            col_map["created_date"] = col
        elif "status" in col_lower:
            col_map["status_code"] = col
    
    if "protocol_number" not in col_map or "type_code" not in col_map or "applicant_name" not in col_map:
        raise HTTPException(status_code=400, detail="Colunas obrigatórias não encontradas: Protocolo, Tipo, Requerente")
    
    imported = 0
    errors = []
    
    # Processar linhas
    for idx, row in df.iterrows():
        try:
            protocol_number = str(row[col_map["protocol_number"]]).strip()
            if pd.isna(row[col_map["protocol_number"]]) or protocol_number == "None" or not protocol_number:
                continue
            
            # Verificar se já existe
            existing = db.query(models.Process).filter(
                models.Process.protocol_number == protocol_number
            ).first()
            if existing:
                continue
            
            type_code = str(row[col_map["type_code"]]).strip().upper()
            applicant_name = str(row[col_map["applicant_name"]]).strip()
            
            applicant_registration = None
            if "applicant_registration" in col_map and not pd.isna(row[col_map["applicant_registration"]]):
                applicant_registration = str(row[col_map["applicant_registration"]]).strip()
            
            status_code = "RECEBIDO"
            if "status_code" in col_map and not pd.isna(row[col_map["status_code"]]):
                status_code = str(row[col_map["status_code"]]).strip().upper()
            
            # Data de criação
            created_date = date.today()
            if "created_date" in col_map and not pd.isna(row[col_map["created_date"]]):
                try:
                    if isinstance(row[col_map["created_date"]], pd.Timestamp):
                        created_date = row[col_map["created_date"]].date()
                    else:
                        date_str = str(row[col_map["created_date"]])
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                            try:
                                created_date = datetime.strptime(date_str.split()[0], fmt).date()
                                break
                            except:
                                continue
                except:
                    created_date = date.today()
            
            # Validar tipo
            process_type = db.query(models.ProcessType).filter(
                models.ProcessType.code == type_code
            ).first()
            if not process_type:
                errors.append(f"Linha {idx+2}: Tipo inválido {type_code}")
                continue
            
            # Validar status
            status = db.query(models.Status).filter(
                models.Status.code == status_code
            ).first()
            if not status:
                status = db.query(models.Status).filter(models.Status.code == "RECEBIDO").first()
            
            # Criar processo
            new_process = models.Process(
                protocol_number=protocol_number,
                type_id=process_type.id,
                applicant_name=applicant_name,
                applicant_registration=applicant_registration if applicant_registration and applicant_registration != "None" else None,
                created_date=created_date,
                status_id=status.id
            )
            db.add(new_process)
            db.flush()
            
            # Criar checklist e prazos
            create_process_checklist(db, new_process.id, process_type.id)
            create_process_deadlines(db, new_process.id, process_type.id, created_date)
            
            imported += 1
        except Exception as e:
            errors.append(f"Linha {idx+2}: {str(e)}")
    
    db.commit()
    
    return {
        "imported": imported,
        "errors": errors[:10],  # Limitar a 10 erros
        "total_errors": len(errors)
    }


@app.post("/api/processes/{protocol}/upload")
async def upload_document(
    protocol: str,
    file: UploadFile = File(...),
    document_code: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Upload de documento anexo a um processo."""
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Salvar arquivo
    file_path, file_size = await utils.save_upload_file(file, process.id)
    
    # Buscar document_id se document_code fornecido
    document_id = None
    process_document_id = None
    if document_code:
        document = db.query(models.Document).filter(
            models.Document.code == document_code
        ).first()
        if document:
            document_id = document.id
            # Buscar ProcessDocument correspondente
            proc_doc = db.query(models.ProcessDocument).filter(
                models.ProcessDocument.process_id == process.id,
                models.ProcessDocument.document_id == document.id
            ).first()
            if proc_doc:
                process_document_id = proc_doc.id
                # Marcar como fornecido
                proc_doc.provided = True
                proc_doc.provided_date = date.today()
    
    # Criar registro de anexo
    attachment = models.DocumentAttachment(
        process_id=process.id,
        document_id=document_id,
        process_document_id=process_document_id,
        filename=file_path.split('/')[-1],
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        uploaded_by=current_user.id,
        description=description
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {
        "message": "Documento enviado com sucesso",
        "attachment_id": attachment.id,
        "filename": file.filename,
        "file_size": file_size
    }


@app.get("/api/processes/{protocol}/attachments")
def list_attachments(
    protocol: str,
    db: Session = Depends(get_db)
):
    """Lista anexos de um processo."""
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    attachments = db.query(models.DocumentAttachment).filter(
        models.DocumentAttachment.process_id == process.id
    ).all()
    
    return [
        {
            "id": att.id,
            "original_filename": att.original_filename,
            "file_size": att.file_size,
            "mime_type": att.mime_type,
            "uploaded_at": str(att.uploaded_at),
            "description": att.description,
            "download_url": f"/api/attachments/{att.id}/download"
        }
        for att in attachments
    ]


@app.get("/api/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db)
):
    """Download de anexo."""
    attachment = db.query(models.DocumentAttachment).filter(
        models.DocumentAttachment.id == attachment_id
    ).first()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    file_path = utils.UPLOAD_DIR / attachment.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=str(file_path),
        filename=attachment.original_filename,
        media_type=attachment.mime_type
    )


# ============ Endpoints de PDF ============

@app.get("/api/processes/{protocol}/report")
def generate_process_report(
    protocol: str,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Gera relatório PDF de um processo."""
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Preparar dados
    process_data = {
        "protocol_number": process.protocol_number,
        "applicant_name": process.applicant_name,
        "type_name": process.process_type.name,
        "status_label": process.status.label,
        "created_date": str(process.created_date),
        "applicant_registration": process.applicant_registration,
        "financial_effective_date": str(process.financial_effective_date) if process.financial_effective_date else None,
        "parecer": process.parecer,
        "documents": [
            {
                "name": doc.document.name,
                "required": doc.required,
                "provided": doc.provided,
                "provided_date": str(doc.provided_date) if doc.provided_date else None
            }
            for doc in process.documents
        ],
        "deadlines": [
            {
                "name": dl.legal_deadline.name,
                "due_date": str(dl.due_date),
                "closed": dl.closed
            }
            for dl in process.deadlines
        ]
    }
    
    # Gerar PDF
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    pdf_path = reports_dir / f"{protocol}_report.pdf"
    
    utils.generate_pdf_report(process_data, str(pdf_path))
    
    return FileResponse(
        path=str(pdf_path),
        filename=f"{protocol}_relatorio.pdf",
        media_type="application/pdf"
    )


# ============ Endpoints de Notificações ============

@app.post("/api/notifications/send")
async def send_notification(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    current_user = Depends(auth.get_current_active_user)
):
    """Envia notificação por email."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem enviar emails")
    
    await utils.send_email(to_email, subject, body, html_body)
    
    return {"message": "Email enviado com sucesso"}


@app.post("/api/processes/{protocol}/notify-deadline")
async def notify_process_deadline(
    protocol: str,
    deadline_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """Envia notificação de prazo vencido para requerente."""
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Buscar prazos vencidos
    today = date.today()
    query = db.query(models.ProcessDeadline).filter(
        models.ProcessDeadline.process_id == process.id,
        models.ProcessDeadline.closed.is_(False),
        models.ProcessDeadline.due_date < today
    )
    
    if deadline_id:
        query = query.filter(models.ProcessDeadline.id == deadline_id)
    
    overdue_deadlines = query.all()
    
    if not overdue_deadlines:
        return {"message": "Nenhum prazo vencido encontrado"}
    
    # Preparar email
    subject = f"PGR - Prazo Vencido - Processo {protocol}"
    body = f"""
Prezado(a) {process.applicant_name},

Informamos que o(s) seguinte(s) prazo(s) do processo {protocol} está(ão) vencido(s):

"""
    for dl in overdue_deadlines:
        days_overdue = (today - dl.due_date).days
        body += f"- {dl.legal_deadline.name}: Vencido há {days_overdue} dia(s) (data limite: {dl.due_date})\n"
        # Marcar como notificado
        dl.notified = True
    
    body += f"""

Atenciosamente,
Sistema PGR
"""
    
    # Em produção, buscar email do requerente de algum lugar
    # Por enquanto, vamos apenas marcar como notificado
    db.commit()
    
    # Se houver email configurado, enviar
    # await utils.send_email(requerente_email, subject, body)
    
    return {
        "message": f"{len(overdue_deadlines)} prazo(s) marcado(s) como notificado(s)",
        "notified_count": len(overdue_deadlines)
    }


# ============ Servir Frontend React ============

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Serve o frontend React para todas as rotas que não são API."""
    # Não servir se for uma rota de API, assets ou docs
    if full_path.startswith("api/") or full_path.startswith("assets/") or full_path.startswith("docs"):
        raise HTTPException(status_code=404)
    
    # Tentar servir React buildado
    if frontend_dist_path.exists() and (frontend_dist_path / "index.html").exists():
        index_path = frontend_dist_path / "index.html"
        return FileResponse(str(index_path))
    
    # Fallback: se frontend antigo existir, servir ele
    if frontend_old_path.exists() and (frontend_old_path / "index.html").exists():
        index_path = frontend_old_path / "index.html"
        return FileResponse(str(index_path))
    
    # Se nenhum frontend existe, retornar mensagem útil
    return {
        "message": "Sistema PGR API está funcionando!",
        "status": "ok",
        "frontend": "não encontrado",
        "docs": "/docs",
        "note": "Frontend React precisa ser buildado. Execute 'npm run build' no frontend-react"
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
