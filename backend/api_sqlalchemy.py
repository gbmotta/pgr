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
from fastapi import FastAPI, HTTPException, Depends, Query, UploadFile, File, Form, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, timedelta, datetime
from pathlib import Path
import os
import json
import pandas as pd
import io

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

# Inicializar banco de dados - será feito lazy na primeira requisição
# Isso evita crashes na inicialização
engine = None

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

# Servir frontend React completo (para SPA routing)
if frontend_dist_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist_path)), name="static")

# Fallback para frontend antigo
if frontend_old_path.exists():
    app.mount("/pgr", StaticFiles(directory=str(frontend_old_path), html=True), name="pgr")

# Importar utilitários e auth
try:
    from backend import auth
    from backend import utils
    from backend import google_drive_utils
except ImportError:
    try:
        from . import auth
        from . import utils
        from . import google_drive_utils
    except ImportError:
        import auth
        import utils
        import google_drive_utils


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


class GoogleDriveLinkSchema(BaseModel):
    url: str


# ============ Schemas de Processos ============

class ProcessCreateSchema(BaseModel):
    """
    Schema para criação de novo processo.
    Adaptado conforme tabela de controle de processos 2026.
    """
    # IDs de identificação
    processo_adm_1doc: Optional[str] = None  # PROCESSO ADM 1DOC
    processo_judicial: Optional[str] = None  # PROCESSO JUDICIAL
    
    # Informações principais
    partes: Optional[str] = None  # PARTES
    tema_observacoes: Optional[str] = None  # TEMA – OBSERVAÇÕES
    
    # Datas e prazos
    data_recebimento_mes_ano: Optional[str] = None  # DATA RECEBIMENTO (MÊS/ANO) - ex: "DEZ/2025"
    prazo_info_estag: Optional[str] = None  # PRAZO INFO – ESTAG (DIA/MÊS) - ex: "13/02"
    prazo_final: Optional[str] = None  # PRAZO FINAL (DD/MM) - ex: "16/02"
    tipo_ato: Optional[str] = None  # TIPO DE ATO (PETIÇÃO OU PARECER OU SEM ATO)
    data_realizacao_ato: Optional[str] = None  # DATA DE REALIZAÇÃO DO ATO (DD/MM/AAAA)
    
    # Campos legados (para compatibilidade)
    protocol_number: Optional[str] = None
    type_code: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_registration: Optional[str] = None
    created_date: Optional[str] = None
    status_code: str = "RECEBIDO"
    notes: Optional[str] = None


class ProcessResponseSchema(BaseModel):
    """
    Schema de resposta com dados do processo.
    Adaptado conforme tabela de controle de processos 2026.
    """
    id: int
    processo_adm_1doc: Optional[str] = None
    processo_judicial: Optional[str] = None
    partes: Optional[str] = None
    tema_observacoes: Optional[str] = None
    data_recebimento_mes_ano: Optional[str] = None
    prazo_info_estag: Optional[str] = None
    prazo_final: Optional[str] = None
    tipo_ato: Optional[str] = None
    data_realizacao_ato: Optional[str] = None
    prazo_color: Optional[str] = None  # Cor calculada: green, yellow, orange, red
    
    # Campos legados
    protocol_number: Optional[str] = None
    type_code: Optional[str] = None
    applicant_name: Optional[str] = None
    created_date: Optional[str] = None
    status_code: Optional[str] = None
    financial_effective_date: Optional[str] = None
    
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
    global engine
    if engine is None:
        engine = models.get_engine()
        models.create_tables(engine)
    
    db = models.get_session(engine)
    try:
        yield db  # Injeta a sessão no endpoint
    finally:
        db.close()  # Fecha a sessão após a requisição


# ============ Funções Auxiliares ============

def calculate_prazo_color(prazo_final: Optional[str]) -> Optional[str]:
    """
    Calcula a cor do prazo baseado na proximidade da data.
    
    Cores:
    - VERDE: Mais de 15 dias para vencer
    - AMARELO: Entre 8 e 15 dias para vencer
    - LARANJA: Entre 1 e 7 dias para vencer
    - VERMELHO: Vencido ou vencendo hoje
    
    Args:
        prazo_final: String no formato "DD/MM" (ex: "16/02")
    
    Returns:
        String com a cor: "green", "yellow", "orange", "red" ou None
    """
    if not prazo_final or not prazo_final.strip():
        return None
    
    try:
        # Parse da data no formato DD/MM
        parts = prazo_final.strip().split('/')
        if len(parts) != 2:
            return None
        
        day = int(parts[0])
        month = int(parts[1])
        
        # Obter ano atual
        today = datetime.now().date()
        year = today.year
        
        # Criar data do prazo (assumindo ano atual)
        prazo_date = date(year, month, day)
        
        # Se a data já passou neste ano, considerar próximo ano
        if prazo_date < today:
            prazo_date = date(year + 1, month, day)
        
        # Calcular diferença em dias
        days_diff = (prazo_date - today).days
        
        # Determinar cor baseado na proximidade
        if days_diff < 0:
            return "red"  # Vencido
        elif days_diff == 0:
            return "red"  # Vencendo hoje
        elif days_diff <= 7:
            return "orange"  # 1 a 7 dias
        elif days_diff <= 15:
            return "yellow"  # 8 a 15 dias
        else:
            return "green"  # Mais de 15 dias
            
    except (ValueError, IndexError):
        return None


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
    Endpoint raiz - tenta servir frontend React ou retorna info da API.
    """
    try:
        # Tentar servir React primeiro
        if frontend_dist_path.exists() and (frontend_dist_path / "index.html").exists():
            return FileResponse(
                str(frontend_dist_path / "index.html"),
                media_type="text/html"
            )
        
        # Fallback para frontend antigo
        if frontend_old_path.exists() and (frontend_old_path / "index.html").exists():
            return FileResponse(
                str(frontend_old_path / "index.html"),
                media_type="text/html"
            )
    except Exception as e:
        import logging
        logging.warning(f"Erro ao servir frontend: {e}")
        # Continuar e retornar JSON se falhar
    
    # Se nenhum frontend, retornar info da API
    return {
        "message": "PGR API - Sistema de Processos Administrativos",
        "version": "3.0.0",
        "orm": "SQLAlchemy",
        "docs": "/docs",
        "status": "running",
        "frontend": "not built yet"
    }


# Catch-all route para React Router (deve ser o último, após todos os outros endpoints)
# Este endpoint será adicionado no final do arquivo, após todas as rotas da API


@app.get("/health")
def health_check():
    """
    Verifica se a API está funcionando.
    """
    try:
        # Tenta conectar ao banco
        test_engine = models.get_engine()
        test_db = models.get_session(test_engine)
        test_db.query(models.ProcessType).first()
        test_db.close()
        return {"status": "healthy", "database": "connected", "api": "running"}
    except Exception as e:
        # Retorna status mesmo com erro no banco
        return {"status": "degraded", "database": "error", "api": "running", "error": str(e)}


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
    # 1. Validar tipo de processo (se fornecido)
    process_type = None
    if payload.type_code:
        process_type = db.query(models.ProcessType).filter(
            models.ProcessType.code == payload.type_code
        ).first()
        
        if not process_type:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de processo inválido: {payload.type_code}"
            )
    
    # 2. Validar status (se fornecido, ou usar padrão)
    status = None
    if payload.status_code:
        status = db.query(models.Status).filter(
            models.Status.code == payload.status_code
        ).first()
        
        if not status:
            raise HTTPException(
                status_code=400,
                detail=f"Status inválido: {payload.status_code}"
            )
    
    # 3. Validar que pelo menos um identificador está presente
    if not payload.processo_adm_1doc and not payload.processo_judicial:
        raise HTTPException(
            status_code=400,
            detail="É necessário fornecer PROCESSO ADM 1DOC ou PROCESSO JUDICIAL"
        )
    
    # 4. Verificar se algum ID de processo já existe
    if payload.processo_adm_1doc:
        existing = db.query(models.Process).filter(
            models.Process.processo_adm_1doc == payload.processo_adm_1doc
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"PROCESSO ADM 1DOC já existe: {payload.processo_adm_1doc}"
            )
    
    if payload.processo_judicial:
        existing = db.query(models.Process).filter(
            models.Process.processo_judicial == payload.processo_judicial
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"PROCESSO JUDICIAL já existe: {payload.processo_judicial}"
            )
    
    # Verificar protocol_number se fornecido (legado)
    if payload.protocol_number:
        existing = db.query(models.Process).filter(
            models.Process.protocol_number == payload.protocol_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Protocolo já existe: {payload.protocol_number}"
            )
    
    # 5. Definir data de criação (hoje se não informada)
    created_date = date.fromisoformat(payload.created_date) if payload.created_date else date.today()
    
    # 6. Gerar protocol_number se não fornecido (usar primeiro identificador disponível)
    protocol_number = payload.protocol_number
    if not protocol_number:
        identifier = payload.processo_adm_1doc or payload.processo_judicial
        protocol_number = identifier or f"PGR-{date.today().year}-{db.query(models.Process).count() + 1:04d}"
    
    # 7. Criar o processo (campos DOCX como primários)
    new_process = models.Process(
        # Campos DOCX canônicos
        processo_adm_1doc=payload.processo_adm_1doc,
        processo_judicial=payload.processo_judicial,
        partes=payload.partes,
        tema_observacoes=payload.tema_observacoes,
        data_recebimento_mes_ano=payload.data_recebimento_mes_ano,
        prazo_info_estag=payload.prazo_info_estag,
        prazo_final=payload.prazo_final,
        tipo_ato=payload.tipo_ato,
        data_realizacao_ato=payload.data_realizacao_ato,
        # Campos legados (compatibilidade)
        protocol_number=protocol_number,
        type_id=process_type.id if process_type else None,
        applicant_name=payload.applicant_name,
        applicant_registration=payload.applicant_registration,
        created_date=created_date,
        status_id=status.id if status else None,
        notes=payload.notes
    )
    
    db.add(new_process)
    db.commit()
    db.refresh(new_process)
    
    # 8. Registrar criação no histórico de auditoria
    from backend import audit_service
    process_data_dict = {
        'processo_adm_1doc': payload.processo_adm_1doc,
        'processo_judicial': payload.processo_judicial,
        'partes': payload.partes,
        'tema_observacoes': payload.tema_observacoes,
        'data_recebimento_mes_ano': payload.data_recebimento_mes_ano,
        'prazo_info_estag': payload.prazo_info_estag,
        'prazo_final': payload.prazo_final,
        'tipo_ato': payload.tipo_ato,
        'data_realizacao_ato': payload.data_realizacao_ato,
        'protocol_number': protocol_number,
        'applicant_name': payload.applicant_name,
        'applicant_registration': payload.applicant_registration,
        'created_date': created_date,
        'notes': payload.notes
    }
    audit_service.AuditService.record_process_creation(
        db=db,
        process_id=new_process.id,
        process_data=process_data_dict,
        change_source='api',
        changed_by_user_id=None  # TODO: get from auth context
    )
    
    # 9. Gerar checklist de documentos (apenas se tiver tipo)
    if process_type:
        create_process_checklist(db, new_process.id, process_type.id)
    
    # 10. Gerar prazos legais (apenas se tiver tipo)
    if process_type and created_date:
        create_process_deadlines(db, new_process.id, process_type.id, created_date)
    
    # 10. Calcular cor do prazo
    prazo_color = calculate_prazo_color(new_process.prazo_final)
    
    # 11. Retornar resposta
    return ProcessResponseSchema(
        id=new_process.id,
        # Novos campos
        processo_adm_1doc=new_process.processo_adm_1doc,
        processo_judicial=new_process.processo_judicial,
        partes=new_process.partes,
        tema_observacoes=new_process.tema_observacoes,
        data_recebimento_mes_ano=new_process.data_recebimento_mes_ano,
        prazo_info_estag=new_process.prazo_info_estag,
        prazo_final=new_process.prazo_final,
        tipo_ato=new_process.tipo_ato,
        data_realizacao_ato=new_process.data_realizacao_ato,
        prazo_color=prazo_color,
        # Campos legados
        protocol_number=new_process.protocol_number,
        type_code=process_type.code if process_type else None,
        applicant_name=new_process.applicant_name,
        created_date=str(new_process.created_date) if new_process.created_date else None,
        status_code=status.code if status else None,
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
    # Query base - sem JOIN obrigatório porque type_id e status_id podem ser None
    query = db.query(models.Process)
    
    # Aplicar filtros se fornecidos (com LEFT JOIN)
    if type_code:
        query = query.join(models.ProcessType, isouter=True).filter(models.ProcessType.code == type_code)
    
    if status_code:
        query = query.join(models.Status, isouter=True).filter(models.Status.code == status_code)
    
    # Ordenar por ID (mais recentes primeiro) ou por prazo_final
    query = query.order_by(models.Process.id.desc())
    
    # Executar query
    processes = query.all()
    
    # Converter para schema de resposta
    result = []
    for proc in processes:
        try:
            # Calcular cor do prazo
            prazo_color = calculate_prazo_color(proc.prazo_final)
            
            result.append(ProcessResponseSchema(
                id=proc.id,
                # Novos campos
                processo_adm_1doc=proc.processo_adm_1doc,
                processo_judicial=proc.processo_judicial,
                partes=proc.partes,
                tema_observacoes=proc.tema_observacoes,
                data_recebimento_mes_ano=proc.data_recebimento_mes_ano,
                prazo_info_estag=proc.prazo_info_estag,
                prazo_final=proc.prazo_final,
                tipo_ato=proc.tipo_ato,
                data_realizacao_ato=proc.data_realizacao_ato,
                prazo_color=prazo_color,
                # Campos legados
                protocol_number=proc.protocol_number,
                type_code=getattr(proc.process_type, 'code', None) if proc.process_type else None,
                applicant_name=proc.applicant_name,
                created_date=str(proc.created_date) if proc.created_date else None,
                status_code=getattr(proc.status, 'code', None) if proc.status else None,
                financial_effective_date=str(proc.financial_effective_date) if proc.financial_effective_date else None
            ))
        except Exception as e:
            import logging
            logging.error(f"Erro ao processar processo {proc.id}: {e}")
            continue
    
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
        # Novos campos do modelo
        "processo_adm_1doc": process.processo_adm_1doc,
        "processo_judicial": process.processo_judicial,
        "partes": process.partes,
        "tema_observacoes": process.tema_observacoes,
        "data_recebimento_mes_ano": process.data_recebimento_mes_ano,
        "prazo_info_estag": process.prazo_info_estag,
        "prazo_final": process.prazo_final,
        "tipo_ato": process.tipo_ato,
        "data_realizacao_ato": process.data_realizacao_ato,
        # Campos legados
        "type": {
            "code": process.process_type.code if process.process_type else None,
            "name": process.process_type.name if process.process_type else None
        },
        "applicant_name": process.applicant_name,
        "applicant_registration": process.applicant_registration,
        "created_date": str(process.created_date) if process.created_date else None,
        "status": {
            "code": process.status.code if process.status else None,
            "label": process.status.label if process.status else None
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


@app.get("/api/processes/deadline-status")
def get_processes_deadline_status(
    alert_window_days: int = Query(7, ge=1, le=90, description="Janela de alerta em dias"),
    include_ok: bool = Query(False, description="Incluir processos com status OK"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna processos com status de prazo calculado.
    
    Útil para destacar visualmente processos com prazos críticos.
    """
    from backend import deadline_awareness
    
    processes = deadline_awareness.get_processes_with_deadline_status(
        db,
        alert_window_days=alert_window_days,
        include_ok=include_ok
    )
    
    return {
        "alert_window_days": alert_window_days,
        "processes": processes,
        "total": len(processes)
    }


@app.get("/api/deadlines/critical")
def get_critical_deadlines(
    alert_window_days: int = Query(7, ge=1, le=90, description="Janela de alerta em dias"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna prazos críticos (vencidos e próximos).
    
    Filtra apenas processos que requerem atenção imediata.
    """
    from backend import deadline_awareness
    
    overdue, upcoming = deadline_awareness.get_critical_deadlines(
        db,
        alert_window_days=alert_window_days
    )
    
    return {
        "alert_window_days": alert_window_days,
        "overdue": overdue,
        "upcoming": upcoming,
        "overdue_count": len(overdue),
        "upcoming_count": len(upcoming)
    }


@app.get("/api/deadlines/alerts")
def get_deadline_alerts(
    alert_window_days: int = Query(7, ge=1, le=90, description="Janela de alerta em dias"),
    min_interval_hours: int = Query(24, ge=1, le=168, description="Intervalo mínimo entre alertas (horas)"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Gera alertas para prazos críticos com controle de notificações.
    
    Retorna apenas processos que:
    - Têm prazos críticos (vencidos ou próximos)
    - Não foram alertados recentemente (respeitando intervalo mínimo)
    - Requerem atenção imediata
    
    Previne notificações excessivas através de rate limiting.
    """
    from backend import alert_service
    
    alerts = alert_service.AlertService.generate_alerts(
        db,
        alert_window_days=alert_window_days,
        min_interval_hours=min_interval_hours
    )
    
    return {
        "alert_window_days": alert_window_days,
        "min_interval_hours": min_interval_hours,
        **alerts
    }


@app.get("/api/processes/{process_id}/history")
def get_process_history(
    process_id: int,
    field_name: Optional[str] = Query(None, description="Filtrar por campo específico"),
    change_source: Optional[str] = Query(None, description="Filtrar por origem (upload, google_sheets, manual, api)"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna histórico de mudanças de um processo.
    
    Fornece trilha de auditoria completa para rastreabilidade legal.
    """
    from backend import audit_service
    import json
    
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    history = audit_service.AuditService.get_process_history(
        db=db,
        process_id=process_id,
        field_name=field_name,
        change_source=change_source,
        limit=limit
    )
    
    return {
        "process_id": process_id,
        "processo_adm_1doc": process.processo_adm_1doc,
        "processo_judicial": process.processo_judicial,
        "protocol_number": process.protocol_number,
        "total_changes": len(history),
        "history": [
            {
                "id": h.id,
                "field_name": h.field_name,
                "field_label": h.field_label,
                "old_value": h.old_value,
                "new_value": h.new_value,
                "change_source": h.change_source,
                "source_details": json.loads(h.source_details) if h.source_details else None,
                "change_type": h.change_type,
                "changed_at": h.changed_at.isoformat(),
                "changed_by_user_id": h.changed_by_user_id,
                "changed_by_username": h.changed_by_user.username if h.changed_by_user else None
            }
            for h in history
        ]
    }


@app.get("/api/processes/{process_id}/history/{field_name}")
def get_field_history(
    process_id: int,
    field_name: str,
    limit: int = Query(50, ge=1, le=200, description="Número máximo de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna histórico de mudanças de um campo específico de um processo.
    
    Útil para rastrear evolução de um campo específico ao longo do tempo.
    """
    from backend import audit_service
    import json
    
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    history = audit_service.AuditService.get_field_history(
        db=db,
        process_id=process_id,
        field_name=field_name,
        limit=limit
    )
    
    return {
        "process_id": process_id,
        "field_name": field_name,
        "field_label": audit_service.AuditService.get_field_label(field_name),
        "current_value": getattr(process, field_name, None),
        "total_changes": len(history),
        "history": [
            {
                "id": h.id,
                "old_value": h.old_value,
                "new_value": h.new_value,
                "change_source": h.change_source,
                "source_details": json.loads(h.source_details) if h.source_details else None,
                "changed_at": h.changed_at.isoformat(),
                "changed_by_user_id": h.changed_by_user_id,
                "changed_by_username": h.changed_by_user.username if h.changed_by_user else None
            }
            for h in history
        ]
    }


@app.get("/api/processes/{process_id}/insights")
def get_process_insights(
    process_id: int,
    include_summary: bool = Query(True, description="Incluir resumos de campos longos"),
    include_prioritization: bool = Query(True, description="Incluir sugestões de priorização"),
    include_risks: bool = Query(True, description="Incluir sinalização de riscos"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna insights assistidos por IA para um processo.
    
    Fornece sugestões e análises sem modificar dados automaticamente.
    
    Insights disponíveis:
    - Priorização baseada em prazos
    - Resumos de campos de observação longos
    - Sinalização de riscos potenciais
    
    IMPORTANTE: Todos os insights são sugestões apenas.
    Nenhum dado é alterado automaticamente.
    """
    from backend import ai_insights
    
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    insights = ai_insights.AIInsightsService.get_process_insights(
        db=db,
        process_id=process_id,
        include_summary=include_summary,
        include_prioritization=include_prioritization,
        include_risks=include_risks
    )
    
    return insights


@app.get("/api/processes/{process_id}/insights/prioritization")
def get_prioritization_suggestion(
    process_id: int,
    alert_window_days: int = Query(7, ge=1, le=90, description="Janela de alerta em dias"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna sugestão de priorização baseada em prazos e contexto.
    """
    from backend import ai_insights
    
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    suggestion = ai_insights.AIInsightsService.suggest_prioritization(
        db=db,
        process_id=process_id,
        alert_window_days=alert_window_days
    )
    
    return suggestion


@app.get("/api/processes/{process_id}/insights/risks")
def get_risk_flags(
    process_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna sinalização de riscos potenciais no processo.
    """
    from backend import ai_insights
    
    process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    risks = ai_insights.AIInsightsService.flag_potential_risks(
        db=db,
        process_id=process_id
    )
    
    return risks


@app.post("/api/processes/insights/summarize")
def summarize_text(
    text: str = Query(..., description="Texto a ser resumido"),
    max_length: int = Query(150, ge=50, le=500, description="Comprimento máximo do resumo"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Resumir texto longo usando IA (se disponível) ou processamento simples.
    
    Útil para resumir campos de observação extensos.
    """
    from backend import ai_insights
    
    summary = ai_insights.AIInsightsService.summarize_observations(
        text=text,
        max_length=max_length
    )
    
    return summary


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


@app.get("/api/stats")
def get_performance_stats(db: Session = Depends(get_db)):
    """
    Retorna estatísticas de performance para o dashboard.
    
    Returns:
        JSON com:
        - total_processos: Total de processos
        - prazos_vencidos: Quantidade de processos com prazo vencido
        - taxa_conclusao: Percentual de processos concluídos
        - media_dias_conclusao: Média de dias para conclusão
        - temas: Agrupamento de processos por tema
        - produtividade_mensal: Processos concluídos por mês
    """
    from collections import defaultdict
    
    today = date.today()
    all_processes = db.query(models.Process).all()
    
    total_processos = len(all_processes)
    
    # Contar prazos vencidos
    prazos_vencidos = 0
    processos_concluidos = 0
    dias_conclusao = []
    temas_count = defaultdict(int)
    produtividade_mensal = defaultdict(int)
    
    for proc in all_processes:
        # Verificar prazo vencido
        if proc.prazo_final:
            try:
                parts = proc.prazo_final.strip().split('/')
                if len(parts) == 2:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = today.year
                    prazo_date = date(year, month, day)
                    
                    if prazo_date < today:
                        prazo_date = date(year + 1, month, day)
                    
                    if prazo_date < today:
                        prazos_vencidos += 1
            except (ValueError, IndexError):
                pass
        
        # Verificar se está concluído
        if proc.data_realizacao_ato:
            processos_concluidos += 1
            
            # Calcular dias para conclusão
            try:
                if proc.created_date:
                    # Tentar parsear data_realizacao_ato (formato DD/MM/AAAA)
                    parts = proc.data_realizacao_ato.strip().split('/')
                    if len(parts) == 3:
                        day = int(parts[0])
                        month = int(parts[1])
                        year = int(parts[2])
                        conclusao_date = date(year, month, day)
                        dias = (conclusao_date - proc.created_date).days
                        if dias > 0:
                            dias_conclusao.append(dias)
                        
                        # Produtividade mensal
                        mes_ano = f"{conclusao_date.strftime('%b')}/{conclusao_date.year}"
                        produtividade_mensal[mes_ano] += 1
            except (ValueError, IndexError, AttributeError):
                pass
        
        # Agrupar por tema
        if proc.tema_observacoes:
            tema_lower = proc.tema_observacoes.lower()
            if 'cível' in tema_lower or 'civil' in tema_lower:
                temas_count['Cível'] += 1
            elif 'trabalhista' in tema_lower or 'trabalho' in tema_lower:
                temas_count['Trabalhista'] += 1
            elif 'administrativo' in tema_lower or 'admin' in tema_lower:
                temas_count['Adm'] += 1
            else:
                temas_count['Outros'] += 1
        else:
            temas_count['Outros'] += 1
    
    # Calcular taxa de conclusão
    taxa_conclusao = (processos_concluidos / total_processos * 100) if total_processos > 0 else 0
    
    # Calcular média de dias para conclusão
    media_dias_conclusao = sum(dias_conclusao) / len(dias_conclusao) if dias_conclusao else 0
    
    # Formatar temas para o gráfico
    temas = [
        {"name": "Cível", "total": temas_count['Cível']},
        {"name": "Trabalhista", "total": temas_count['Trabalhista']},
        {"name": "Adm", "total": temas_count['Adm']},
        {"name": "Outros", "total": temas_count['Outros']}
    ]
    
    # Formatar produtividade mensal (últimos 4 meses)
    meses_ordenados = sorted(produtividade_mensal.items(), key=lambda x: x[0])[-4:]
    produtividade = [
        {"mes": mes.split('/')[0][:3], "concluidos": count}
        for mes, count in meses_ordenados
    ]
    
    return {
        "total_processos": total_processos,
        "prazos_vencidos": prazos_vencidos,
        "taxa_conclusao": round(taxa_conclusao, 1),
        "media_dias_conclusao": round(media_dias_conclusao, 0),
        "temas": temas,
        "produtividade_mensal": produtividade
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
    
    # Converter user para dict (evita problemas com sessão fechada)
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
    }
    
    # Retornar dict - FastAPI usa response_model para serializar
    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseSchema(**user_dict)
    )


@app.get("/api/auth/me", response_model=UserResponseSchema)
def get_current_user_info(current_user = Depends(auth.get_current_active_user)):
    """Retorna informações do usuário logado."""
    # Converter objeto SQLAlchemy para Pydantic usando model_validate (Pydantic v2)
    return UserResponseSchema.model_validate(current_user)


# ============ Endpoints de Upload ============

@app.post("/api/processes/preview-upload")
async def preview_upload_excel(
    file: UploadFile = File(...),
    preview_rows: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Pré-visualização e validação de planilha antes da importação.
    
    Retorna:
    - Preview das primeiras N linhas
    - Validação de cada linha (erros e avisos)
    - Estatísticas de validação
    - Indicação se a importação é permitida
    
    A importação só é permitida se não houver erros críticos.
    """
    from backend import spreadsheet_ingestion
    
    contents = await file.read()
    filename = file.filename or "upload.xlsx"
    
    try:
        preview_result = spreadsheet_ingestion.preview_spreadsheet(
            contents,
            filename,
            preview_rows=preview_rows,
            db_session=db
        )
        
        if "error" in preview_result:
            raise HTTPException(status_code=400, detail=preview_result["error"])
        
        return preview_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar preview: {str(e)}"
        )


@app.post("/api/processes/preview-google-sheets")
async def preview_google_sheets(
    link_data: GoogleDriveLinkSchema,
    preview_rows: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Pré-visualização e validação de planilha do Google Drive antes da importação.
    
    Suporta: Google Sheets, Excel (.xlsx, .xls), CSV, TSV
    
    IMPORTANTE: O arquivo deve ser compartilhado com o Service Account do sistema.
    Use /api/sheets/service-account-email para obter o email necessário.
    """
    from backend import drive_service
    from backend import sheets_service
    from backend import google_auth
    from backend import spreadsheet_ingestion
    
    file_id = google_drive_utils.extract_file_id_from_url(link_data.url)
    if not file_id:
        raise HTTPException(
            status_code=400,
            detail="URL inválida. Por favor, forneça um link válido do Google Drive."
        )
    
    # Aceitar qualquer URL do Google Drive (Google Sheets, Excel, CSV, TSV)
    has_access, file_name, error_message, file_type = drive_service.verify_file_access(file_id)
    
    if not has_access:
        service_account_email = None
        try:
            service_account_email = google_auth.get_service_account_email()
        except Exception:
            pass
        
        detail = {
            "error": "Acesso negado",
            "message": error_message or "Não foi possível acessar a planilha.",
            "file_id": file_id
        }
        
        if service_account_email:
            detail["service_account_email"] = service_account_email
            detail["instructions"] = (
                "Para importar esta planilha:\n"
                f"1. Abra a planilha no Google Sheets\n"
                f"2. Clique em 'Compartilhar'\n"
                f"3. Adicione o email: {service_account_email}\n"
                f"4. Defina a permissão como 'Visualizador'\n"
                f"5. Tente novamente"
            )
        
        raise HTTPException(status_code=403, detail=detail)
    
    # Se for Excel, CSV ou TSV, tentar converter automaticamente para Google Sheets
    converted_to_sheets = False
    original_file_id = file_id
    conversion_error = None
    
    if file_type in ['excel', 'csv', 'tsv']:
        try:
            # Tentar converter para Google Sheets
            new_file_id, new_file_name = drive_service.convert_to_google_sheets(
                file_id, file_type, file_name
            )
            
            # Usar o Google Sheets criado
            file_id = new_file_id
            file_name = new_file_name
            file_type = 'google_sheets'
            converted_to_sheets = True
            
            # Compartilhar automaticamente com o Service Account
            service_account_email = None
            try:
                service_account_email = google_auth.get_service_account_email()
                if service_account_email:
                    drive_service_obj = drive_service.get_drive_service()
                    drive_service_obj.permissions().create(
                        fileId=new_file_id,
                        body={
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': service_account_email
                        },
                        fields='id'
                    ).execute()
            except Exception as e:
                # Log mas não falha se não conseguir compartilhar
                import logging
                logging.warning(f"Erro ao compartilhar Google Sheets criado: {str(e)}")
        except (ValueError, Exception) as e:
            # Erro de conversão (ex: quota excedida) - usar arquivo original sem sincronização
            conversion_error = str(e)
            import logging
            logging.warning(f"Não foi possível converter para Google Sheets: {conversion_error}")
            # Continuar com o arquivo original (sem sincronização dinâmica)
    
    # Baixar arquivo baseado no tipo (pode ser Google Sheets ou original)
    try:
        if file_type == 'google_sheets':
            # Google Sheets: usar Sheets API
            file_content = sheets_service.fetch_sheet_as_excel_bytes(file_id)
            filename = file_name or "planilha_google_sheets.xlsx"
        else:
            # Fallback: baixar diretamente do Drive
            file_content, filename = drive_service.download_file_from_drive(file_id, file_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao baixar arquivo do Google Drive: {str(e)}"
        )
    
    try:
        # Usar o tipo de arquivo correto para preview
        # Se foi convertido, usar 'google_sheets', senão usar o tipo original
        preview_format = 'google_sheets' if converted_to_sheets else file_type
        preview_result = spreadsheet_ingestion.preview_spreadsheet(
            file_content,
            filename,
            file_format=preview_format,
            preview_rows=preview_rows,
            db_session=db
        )
        
        if "error" in preview_result:
            raise HTTPException(status_code=400, detail=preview_result["error"])
        
        # Adicionar informação sobre conversão se aplicável
        if converted_to_sheets and file_id:
            preview_result["google_sheets_url"] = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
            preview_result["converted_to_google_sheets"] = True
            preview_result["original_file_id"] = original_file_id
            if "message" in preview_result:
                preview_result["message"] += " Arquivo convertido automaticamente para Google Sheets para sincronização dinâmica."
            else:
                preview_result["message"] = "Arquivo convertido automaticamente para Google Sheets para sincronização dinâmica."
        elif conversion_error:
            # Se houve erro na conversão, informar mas continuar
            preview_result["conversion_warning"] = conversion_error
            preview_result["sync_available"] = False
            if "message" in preview_result:
                preview_result["message"] += f" Aviso: {conversion_error[:100]}"
            else:
                preview_result["message"] = f"Aviso: {conversion_error[:100]}"
        
        return preview_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar preview: {str(e)}"
        )


@app.post("/processes/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    skip_validation: bool = Query(False, description="Pular validação (não recomendado)"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Upload e importação de processos via planilha (XLSX, CSV).
    Suporta múltiplos formatos mantendo o schema DOCX canônico.
    
    IMPORTANTE: Recomenda-se usar /api/processes/preview-upload primeiro
    para validar os dados antes da importação.
    """
    from backend import spreadsheet_ingestion
    
    contents = await file.read()
    filename = file.filename or "upload.xlsx"
    
    if not skip_validation:
        preview = spreadsheet_ingestion.preview_spreadsheet(
            contents,
            filename,
            preview_rows=20,
            db_session=db
        )
        
        if "error" in preview:
            raise HTTPException(status_code=400, detail=preview["error"])
        
        if not preview.get("can_import", False):
            error_count = preview.get("summary", {}).get("errors", 0)
            raise HTTPException(
                status_code=400,
                detail=f"Importação bloqueada: {error_count} erro(s) crítico(s) encontrado(s). "
                       f"Use /api/processes/preview-upload para ver detalhes."
            )
    
    try:
        df, col_map, missing = spreadsheet_ingestion.ingest_spreadsheet(contents, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")
    
    imported = 0
    skipped = 0
    errors = []
    
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
                continue
            
            identifier = processo_adm_1doc or processo_judicial
            
            existing = None
            if processo_adm_1doc:
                existing = db.query(models.Process).filter(
                    models.Process.processo_adm_1doc == processo_adm_1doc
                ).first()
            if not existing and processo_judicial:
                existing = db.query(models.Process).filter(
                    models.Process.processo_judicial == processo_judicial
                ).first()
            
            if existing:
                skipped += 1
                continue
            
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
                protocol_number=identifier,
                created_date=date.today()
            )
            db.add(new_process)
            db.flush()
            
            # Registrar criação no histórico de auditoria
            try:
                from backend import audit_service
                audit_service.AuditService.record_process_creation(
                    db=db,
                    process_id=new_process.id,
                    process_data=process_data,
                    change_source='upload',
                    source_details={
                        'filename': filename,
                        'row_number': idx + 2,
                        'file_type': 'xlsx'
                    },
                    changed_by_user_id=current_user.id if current_user else None
                )
            except Exception as e:
                # Log error but don't fail import
                import logging
                logging.error(f"Erro ao registrar histórico de auditoria: {e}")
            
            imported += 1
        except Exception as e:
            errors.append({
                "row": idx + 2,
                "message": str(e)
            })
    
    db.commit()
    
    # Preparar resposta
    response_data = {
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:10],
        "total_errors": len(errors),
        "message": f"Importação concluída: {imported} processo(s) importado(s), {skipped} ignorado(s)."
    }
    
    # Se foi convertido para Google Sheets ou já é Google Sheets nativo, incluir informações para monitoramento
    if file_type == 'google_sheets' and file_id:
        response_data["file_id"] = file_id
        response_data["file_name"] = file_name
        response_data["can_monitor"] = True
        # Se foi convertido, incluir o link do Google Sheets criado
        if converted_to_sheets:
            try:
                drive_service_obj = drive_service.get_drive_service()
                file_metadata = drive_service_obj.files().get(
                    fileId=file_id,
                    fields='webViewLink'
                ).execute()
                response_data["google_sheets_url"] = file_metadata.get('webViewLink')
                response_data["converted_to_sheets"] = True
            except Exception:
                # Se não conseguir obter o link, não é crítico
                pass
    elif conversion_error:
        response_data["conversion_warning"] = (
            f"Não foi possível converter para Google Sheets: {conversion_error}. "
            "O arquivo foi importado, mas não será possível monitorar alterações automaticamente."
        )
        response_data["can_monitor"] = False
    
    return response_data


@app.post("/processos/upload")
async def upload_processos(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Upload e importação de processos via planilha Excel ou CSV.
    
    Requisitos:
    - O arquivo deve conter as colunas obrigatórias: 'numero_processo' e 'prazo_final'
    - Suporta formatos: .xlsx, .xls, .csv
    
    Mapeamento de colunas:
    - numero_processo -> processo_adm_1doc (ou protocol_number)
    - prazo_final -> prazo_final (formato DD/MM)
    - partes -> partes (opcional)
    - Outras colunas serão mapeadas conforme disponibilidade
    """
    # Validar tipo de arquivo
    filename = file.filename or "upload.xlsx"
    file_extension = filename.lower().split('.')[-1]
    
    if file_extension not in ['xlsx', 'xls', 'csv']:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de arquivo não suportado: {file_extension}. Use .xlsx, .xls ou .csv"
        )
    
    # Ler conteúdo do arquivo
    contents = await file.read()
    
    # Ler planilha com pandas
    try:
        if file_extension == 'csv':
            # Tentar diferentes encodings para CSV
            try:
                df = pd.read_csv(
                    io.BytesIO(contents),
                    encoding='utf-8-sig',
                    dtype=str,
                    keep_default_na=False
                )
            except UnicodeDecodeError:
                # Tentar com latin-1 se UTF-8 falhar
                df = pd.read_csv(
                    io.BytesIO(contents),
                    encoding='latin-1',
                    dtype=str,
                    keep_default_na=False
                )
        else:
            # Excel (.xlsx, .xls)
            df = pd.read_excel(
                io.BytesIO(contents),
                dtype=str,
                keep_default_na=False,
                engine='openpyxl'
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao ler arquivo: {str(e)}"
        )
    
    # Validar que o DataFrame não está vazio
    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="O arquivo está vazio ou não contém dados"
        )
    
    # Normalizar nomes das colunas (remover espaços, converter para minúsculas)
    df.columns = df.columns.str.strip().str.lower()
    
    # Validar colunas obrigatórias
    required_columns = ['numero_processo', 'prazo_final']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Colunas obrigatórias não encontradas no arquivo: {', '.join(missing_columns)}. "
                   f"Colunas disponíveis: {', '.join(df.columns.tolist())}"
        )
    
    # Processar cada linha
    imported = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Extrair dados da linha
            numero_processo = str(row.get('numero_processo', '')).strip()
            prazo_final = str(row.get('prazo_final', '')).strip()
            partes = str(row.get('partes', '')).strip() or None
            
            # Validar dados obrigatórios
            if not numero_processo:
                errors.append({
                    "row": idx + 2,  # +2 porque idx começa em 0 e há o cabeçalho
                    "message": "Campo 'numero_processo' está vazio"
                })
                continue
            
            if not prazo_final:
                errors.append({
                    "row": idx + 2,
                    "message": "Campo 'prazo_final' está vazio"
                })
                continue
            
            # Verificar se o processo já existe
            existing = db.query(models.Process).filter(
                models.Process.processo_adm_1doc == numero_processo
            ).first()
            
            if not existing:
                # Tentar também por protocol_number
                existing = db.query(models.Process).filter(
                    models.Process.protocol_number == numero_processo
                ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Criar novo processo
            new_process = models.Process(
                processo_adm_1doc=numero_processo,
                protocol_number=numero_processo,
                prazo_final=prazo_final,
                partes=partes,
                created_date=date.today()
            )
            
            # Mapear outras colunas opcionais se existirem
            if 'tema_observacoes' in df.columns:
                new_process.tema_observacoes = str(row.get('tema_observacoes', '')).strip() or None
            
            if 'data_recebimento_mes_ano' in df.columns:
                new_process.data_recebimento_mes_ano = str(row.get('data_recebimento_mes_ano', '')).strip() or None
            
            if 'tipo_ato' in df.columns:
                new_process.tipo_ato = str(row.get('tipo_ato', '')).strip() or None
            
            if 'processo_judicial' in df.columns:
                new_process.processo_judicial = str(row.get('processo_judicial', '')).strip() or None
            
            db.add(new_process)
            imported += 1
            
        except Exception as e:
            errors.append({
                "row": idx + 2,
                "message": f"Erro ao processar linha: {str(e)}"
            })
    
    # Commit das alterações
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar processos no banco de dados: {str(e)}"
        )
    
    # Retornar resultado
    return {
        "message": f"Upload concluído com sucesso",
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:20],  # Limitar a 20 erros na resposta
        "total_errors": len(errors),
        "total_rows": len(df),
        "details": {
            "arquivo": filename,
            "total_linhas_processadas": len(df),
            "sucesso": imported,
            "ignorados": skipped,
            "erros": len(errors)
        }
    }


@app.post("/processes/upload-from-google-drive")
async def upload_from_google_drive(
    link_data: GoogleDriveLinkSchema,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Importa processos via link do Google Sheets.
    
    IMPORTANTE: A planilha deve ser compartilhada com o Service Account do sistema.
    Use /api/sheets/service-account-email para obter o email necessário.
    
    Não é necessário compartilhar como "Qualquer pessoa com o link pode ver".
    """
    import pandas as pd
    import io
    from backend import drive_service
    from backend import sheets_service
    from backend import google_auth
    
    file_id = google_drive_utils.extract_file_id_from_url(link_data.url)
    if not file_id:
        raise HTTPException(
            status_code=400,
            detail="URL inválida. Por favor, forneça um link válido do Google Sheets."
        )
    
    # Aceitar qualquer URL do Google Drive (Google Sheets, Excel, CSV, TSV)
    # Se for Excel/CSV/TSV, converteremos automaticamente para Google Sheets
    
    has_access, file_name, error_message, file_type = drive_service.verify_file_access(file_id)
    
    if not has_access:
        service_account_email = None
        try:
            service_account_email = google_auth.get_service_account_email()
        except Exception:
            pass
        
        detail = {
            "error": "Acesso negado",
            "message": error_message or "Não foi possível acessar o arquivo.",
            "file_id": file_id
        }
        
        if service_account_email:
            detail["service_account_email"] = service_account_email
            detail["instructions"] = (
                "Para importar este arquivo:\n"
                f"1. Abra o arquivo no Google Drive\n"
                f"2. Clique em 'Compartilhar'\n"
                f"3. Adicione o email: {service_account_email}\n"
                f"4. Defina a permissão como 'Visualizador'\n"
                f"5. Tente novamente"
            )
        
        raise HTTPException(status_code=403, detail=detail)
    
    # Se for Excel, CSV ou TSV, tentar converter automaticamente para Google Sheets
    converted_to_sheets = False
    original_file_id = file_id
    conversion_error = None
    
    if file_type in ['excel', 'csv', 'tsv']:
        try:
            # Tentar converter para Google Sheets
            new_file_id, new_file_name = drive_service.convert_to_google_sheets(
                file_id, file_type, file_name
            )
            
            # Usar o Google Sheets criado
            file_id = new_file_id
            file_name = new_file_name
            file_type = 'google_sheets'
            converted_to_sheets = True
            
            # Compartilhar automaticamente com o Service Account
            service_account_email = None
            try:
                service_account_email = google_auth.get_service_account_email()
                if service_account_email:
                    drive_service_obj = drive_service.get_drive_service()
                    drive_service_obj.permissions().create(
                        fileId=new_file_id,
                        body={
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': service_account_email
                        },
                        fields='id'
                    ).execute()
            except Exception as e:
                # Log mas não falha se não conseguir compartilhar
                import logging
                logging.warning(f"Erro ao compartilhar Google Sheets criado: {str(e)}")
        except (ValueError, Exception) as e:
            # Erro de conversão (ex: quota excedida) - usar arquivo original sem sincronização
            conversion_error = str(e)
            import logging
            logging.warning(f"Não foi possível converter para Google Sheets: {conversion_error}")
            # Continuar com o arquivo original (sem sincronização dinâmica)
    
    # Baixar arquivo baseado no tipo (pode ser Google Sheets ou original)
    try:
        if file_type == 'google_sheets':
            # Google Sheets: usar Sheets API
            file_content = sheets_service.fetch_sheet_as_excel_bytes(file_id)
            filename = file_name or "planilha_google_sheets.xlsx"
        else:
            # Fallback: baixar diretamente do Drive
            file_content, filename = drive_service.download_file_from_drive(file_id, file_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao baixar arquivo do Google Drive: {str(e)}"
        )
    
    from backend import ingestion
    
    try:
        # Usar o tipo de arquivo correto para ingestão (agora sempre google_sheets)
        ingestion_format = 'google_sheets'
        df, col_map, missing = ingestion.ingest_spreadsheet(file_content, filename, ingestion_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar planilha: {str(e)}")
    
    imported = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            process_data = ingestion.extract_process_row(row, col_map)
            
            is_valid, error_msg = ingestion.validate_process_data(process_data)
            if not is_valid:
                errors.append(f"Linha {idx+2}: {error_msg}")
                continue
            
            processo_adm_1doc = process_data.get('processo_adm_1doc')
            processo_judicial = process_data.get('processo_judicial')
            identifier = processo_adm_1doc or processo_judicial
            
            existing = None
            if processo_adm_1doc:
                existing = db.query(models.Process).filter(
                    models.Process.processo_adm_1doc == processo_adm_1doc
                ).first()
            if not existing and processo_judicial:
                existing = db.query(models.Process).filter(
                    models.Process.processo_judicial == processo_judicial
                ).first()
            
            if existing:
                skipped += 1
                continue
            
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
                protocol_number=identifier,
                created_date=date.today()
            )
            db.add(new_process)
            db.flush()
            
            # Registrar criação no histórico de auditoria
            try:
                from backend import audit_service
                audit_service.AuditService.record_process_creation(
                    db=db,
                    process_id=new_process.id,
                    process_data=process_data,
                    change_source='google_sheets',
                    source_details={
                        'file_id': file_id,
                        'filename': filename,
                        'row_number': idx + 2,
                        'file_type': 'google_sheets'
                    },
                    changed_by_user_id=current_user.id if current_user else None
                )
            except Exception as e:
                # Log error but don't fail import
                import logging
                logging.error(f"Erro ao registrar histórico de auditoria: {e}")
            
            imported += 1
        except Exception as e:
            errors.append(f"Linha {idx+2}: {str(e)}")
    
    db.commit()
    
    response = {
        "imported": imported,
        "skipped": skipped,  # Processos que já existiam
        "errors": errors[:10],  # Limitar a 10 erros
        "total_errors": len(errors),
        "source": "google_drive",
        "filename": filename
    }
    
    # Se foi convertido para Google Sheets ou já é Google Sheets nativo, incluir informações para monitoramento
    if file_type == 'google_sheets' and file_id:
        response["google_sheets_url"] = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
        response["file_id"] = file_id
        response["file_name"] = file_name
        response["can_monitor"] = True
        
        if converted_to_sheets:
            response["converted_to_google_sheets"] = True
            response["original_file_id"] = original_file_id
            response["message"] = f"{imported} processo(s) importado(s), {skipped} ignorado(s). Arquivo convertido automaticamente para Google Sheets para sincronização dinâmica."
        else:
            response["message"] = f"{imported} processo(s) importado(s), {skipped} ignorado(s)."
    elif conversion_error:
        # Se houve erro na conversão, informar mas continuar
        response["conversion_warning"] = conversion_error
        response["can_monitor"] = False
        response["sync_available"] = False
        response["message"] = f"{imported} processo(s) importado(s), {skipped} ignorado(s). Importação realizada, mas sincronização dinâmica não está disponível (erro na conversão)."
    else:
        # Arquivo não é Google Sheets e não foi convertido (ex: Excel/CSV que não pode converter)
        response["can_monitor"] = False
        response["message"] = f"{imported} processo(s) importado(s), {skipped} ignorado(s)."
    
    return response


@app.put("/api/processes/{protocol}/documents/{document_code}")
def update_document_checklist(
    protocol: str,
    document_code: str,
    provided: bool = Query(..., description="Se o documento foi fornecido"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Atualiza o status de um documento no checklist do processo.
    
    Args:
        protocol: Número do protocolo do processo
        document_code: Código do documento (ex: 'RG', 'CPF')
        provided: True se o documento foi fornecido, False caso contrário
        db: Sessão do banco
        current_user: Usuário autenticado
    
    Returns:
        Status atualizado do documento
    """
    # Buscar processo
    process = db.query(models.Process).filter(
        models.Process.protocol_number == protocol
    ).first()
    
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Buscar documento
    document = db.query(models.Document).filter(
        models.Document.code == document_code
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    # Buscar ProcessDocument (checklist)
    proc_doc = db.query(models.ProcessDocument).filter(
        models.ProcessDocument.process_id == process.id,
        models.ProcessDocument.document_id == document.id
    ).first()
    
    if not proc_doc:
        # Criar entrada no checklist se não existir
        proc_doc = models.ProcessDocument(
            process_id=process.id,
            document_id=document.id,
            required=False,
            provided=provided,
            provided_date=date.today() if provided else None
        )
        db.add(proc_doc)
    else:
        # Atualizar status
        proc_doc.provided = provided
        proc_doc.provided_date = date.today() if provided else None
    
    db.commit()
    db.refresh(proc_doc)
    
    return {
        "message": "Checklist atualizado com sucesso",
        "document": {
            "code": document.code,
            "name": document.name,
            "provided": proc_doc.provided,
            "provided_date": str(proc_doc.provided_date) if proc_doc.provided_date else None
        }
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
    
    # Preparar email (subject será usado quando envio de email for implementado)
    subject = f"PGR - Prazo Vencido - Processo {protocol}"  # noqa: F841
    body = f"""
Prezado(a) {process.applicant_name},

Informamos que o(s) seguinte(s) prazo(s) do processo {protocol} está(ão) vencido(s):

"""
    for dl in overdue_deadlines:
        days_overdue = (today - dl.due_date).days
        body += f"- {dl.legal_deadline.name}: Vencido há {days_overdue} dia(s) (data limite: {dl.due_date})\n"
        # Marcar como notificado
        dl.notified = True
    
    body += """
    
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


# ============ Google Drive Webhook Endpoint ============

@app.post("/api/webhooks/google-drive")
async def google_drive_webhook(
    request: Request,
    x_goog_channel_id: str = Header(..., alias='X-Goog-Channel-Id'),
    x_goog_resource_id: str = Header(..., alias='X-Goog-Resource-Id'),
    x_goog_resource_state: str = Header(..., alias='X-Goog-Resource-State'),
    x_goog_channel_token: Optional[str] = Header(None, alias='X-Goog-Channel-Token'),
    x_goog_resource_uri: Optional[str] = Header(None, alias='X-Goog-Resource-Uri'),
    x_goog_changed: Optional[str] = Header(None, alias='X-Goog-Changed')
):
    """
    Webhook endpoint for Google Drive change notifications.
    
    This endpoint receives notifications when linked Google Sheets are modified.
    Automatically synchronizes data when changes are detected.
    """
    from backend import webhook_handler
    return await webhook_handler.handle_drive_webhook(
        request,
        x_goog_channel_id,
        x_goog_channel_token,
        x_goog_resource_id,
        x_goog_resource_state,
        x_goog_resource_uri,
        x_goog_changed
    )


@app.get("/api/sheets/{file_id}/sync-history")
async def get_sync_history(
    file_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Retorna o histórico de sincronizações de uma planilha vinculada.
    
    Args:
        file_id: ID do arquivo Google Sheets
        limit: Número máximo de registros a retornar (padrão: 20)
        
    Returns:
        Lista de histórico de sincronizações ordenada por data (mais recente primeiro)
    """
    linked_sheet = db.query(models.LinkedSheet).filter(
        models.LinkedSheet.file_id == file_id,
        models.LinkedSheet.is_active == True
    ).first()
    
    if not linked_sheet:
        raise HTTPException(status_code=404, detail="Planilha não encontrada ou inativa")
    
    history = db.query(models.SheetSyncHistory).filter(
        models.SheetSyncHistory.linked_sheet_id == linked_sheet.id
    ).order_by(
        models.SheetSyncHistory.sync_started_at.desc()
    ).limit(limit).all()
    
    return {
        "file_id": file_id,
        "linked_sheet_id": linked_sheet.id,
        "url": linked_sheet.url,
        "last_sync": linked_sheet.last_sync.isoformat() if linked_sheet.last_sync else None,
        "history": [
            {
                "id": h.id,
                "sync_started_at": h.sync_started_at.isoformat(),
                "sync_completed_at": h.sync_completed_at.isoformat() if h.sync_completed_at else None,
                "status": h.status,
                "rows_processed": h.rows_processed,
                "rows_imported": h.rows_imported,
                "rows_updated": h.rows_updated,
                "rows_skipped": h.rows_skipped,
                "errors_count": h.errors_count,
                "error_message": h.error_message,
                "sync_details": json.loads(h.sync_details) if h.sync_details else None,
                "duration_seconds": (
                    (h.sync_completed_at - h.sync_started_at).total_seconds()
                    if h.sync_completed_at and h.sync_started_at
                    else None
                )
            }
            for h in history
        ],
        "total": len(history)
    }


# ============ Google Sheets Link Management ============

@app.post("/api/sheets/link")
async def link_google_sheet(
    link_data: GoogleDriveLinkSchema,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Link a Google Sheet for dynamic updates via webhooks.
    
    Validates access and creates a watch channel.
    Clients only need to share the spreadsheet with the Service Account email.
    """
    from backend import drive_service
    from backend import google_drive_utils
    from backend import google_auth
    from datetime import datetime
    
    file_id = google_drive_utils.extract_file_id_from_url(link_data.url)
    if not file_id:
        raise HTTPException(
            status_code=400,
            detail="URL inválida. Por favor, forneça um link válido do Google Sheets."
        )
    
    # Aceitar qualquer URL do Google Drive (Google Sheets, Excel, CSV, TSV)
    # Mas apenas Google Sheets suporta sincronização dinâmica
    
    has_access, file_name, error_message, file_type = drive_service.verify_file_access(file_id)
    
    if not has_access:
        service_account_email = None
        try:
            service_account_email = google_auth.get_service_account_email()
        except Exception:
            pass
        
        detail = {
            "error": "Acesso negado",
            "message": error_message or "Não foi possível acessar o arquivo.",
            "file_id": file_id
        }
        
        if service_account_email:
            detail["service_account_email"] = service_account_email
            detail["instructions"] = (
                "Para vincular este arquivo:\n"
                f"1. Abra o arquivo no Google Drive\n"
                f"2. Clique em 'Compartilhar'\n"
                f"3. Adicione o email: {service_account_email}\n"
                f"4. Defina a permissão como 'Visualizador'\n"
                f"5. Tente novamente"
            )
        
        raise HTTPException(status_code=403, detail=detail)
    
    # Apenas Google Sheets nativos suportam sincronização dinâmica
    # Se for Excel, CSV ou TSV, tentar converter automaticamente para Google Sheets
    if file_type in ['excel', 'csv', 'tsv']:
        try:
            # Tentar converter para Google Sheets
            new_file_id, new_file_name = drive_service.convert_to_google_sheets(
                file_id, file_type, file_name
            )
            
            # Usar o Google Sheets criado
            file_id = new_file_id
            file_name = new_file_name
            file_type = 'google_sheets'
            
            # Compartilhar automaticamente com o Service Account
            service_account_email = None
            try:
                service_account_email = google_auth.get_service_account_email()
                if service_account_email:
                    drive_service_obj = drive_service.get_drive_service()
                    drive_service_obj.permissions().create(
                        fileId=new_file_id,
                        body={
                            'type': 'user',
                            'role': 'reader',
                            'emailAddress': service_account_email
                        },
                        fields='id'
                    ).execute()
            except Exception as e:
                # Log mas não falha se não conseguir compartilhar
                import logging
                logging.warning(f"Erro ao compartilhar Google Sheets criado: {str(e)}")
        except ValueError as e:
            # Erro de conversão (ex: quota excedida) - não podemos vincular sem Google Sheets
            error_msg = str(e)
            if 'storageQuotaExceeded' in error_msg or 'quota' in error_msg.lower():
                raise HTTPException(
                    status_code=507,  # 507 Insufficient Storage
                    detail={
                        "error": "Cota de armazenamento excedida",
                        "message": (
                            "Não foi possível converter o arquivo para Google Sheets porque a cota de armazenamento "
                            "do Service Account foi excedida. Para vincular para sincronização dinâmica, você precisa:\n"
                            "1. Liberar espaço no Google Drive do Service Account, ou\n"
                            "2. Converter manualmente o arquivo para Google Sheets e compartilhar o Google Sheets nativo"
                        ),
                        "original_error": error_msg
                    }
                )
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao converter arquivo para Google Sheets: {error_msg}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao converter arquivo para Google Sheets: {str(e)}"
            )
    
    # Agora sempre será Google Sheets, então pode criar watch channel
    
    webhook_url = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:8001') + '/api/webhooks/google-drive'
    
    try:
        channel_info = drive_service.create_watch_channel(
            file_id=file_id,
            webhook_url=webhook_url,
            expiration_hours=168
        )
        
        existing = db.query(models.LinkedSheet).filter(
            models.LinkedSheet.file_id == file_id
        ).first()
        
        if existing:
            existing.channel_id = channel_info['channel_id']
            existing.resource_id = channel_info['resource_id']
            existing.expiration = datetime.fromtimestamp(channel_info['expiration'] / 1000)
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
        else:
            linked_sheet = models.LinkedSheet(
                file_id=file_id,
                url=link_data.url,
                channel_id=channel_info['channel_id'],
                resource_id=channel_info['resource_id'],
                expiration=datetime.fromtimestamp(channel_info['expiration'] / 1000),
                is_active=True
            )
            db.add(linked_sheet)
        
        db.commit()
        
        return {
            "status": "linked",
            "file_id": file_id,
            "file_name": file_name,
            "channel_id": channel_info['channel_id'],
            "expiration": channel_info['expiration'],
            "message": f"Planilha '{file_name}' vinculada com sucesso. Alterações serão sincronizadas automaticamente."
        }
    except ValueError as e:
        error_msg = str(e)
        if "watch" in error_msg.lower() or "channel" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Erro ao criar canal de notificação. Verifique se a planilha está acessível e tente novamente."
            )
        raise HTTPException(status_code=500, detail=f"Erro ao vincular planilha: {error_msg}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado ao vincular planilha: {str(e)}"
        )


@app.delete("/api/sheets/link/{file_id}")
async def unlink_google_sheet(
    file_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Unlink a Google Sheet and stop watch channel.
    """
    from backend import drive_service
    
    linked_sheet = db.query(models.LinkedSheet).filter(
        models.LinkedSheet.file_id == file_id
    ).first()
    
    if not linked_sheet:
        raise HTTPException(status_code=404, detail="Linked sheet not found")
    
    if linked_sheet.resource_id:
        drive_service.stop_watch_channel(linked_sheet.resource_id)
    
    linked_sheet.is_active = False
    db.commit()
    
    return {"status": "unlinked", "file_id": file_id}


@app.get("/api/sheets/linked")
async def list_linked_sheets(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    List all linked Google Sheets.
    """
    linked_sheets = db.query(models.LinkedSheet).filter(
        models.LinkedSheet.is_active == True
    ).all()
    
    return [
        {
            "id": sheet.id,
            "file_id": sheet.file_id,
            "url": sheet.url,
            "last_sync": sheet.last_sync.isoformat() if sheet.last_sync else None,
            "expiration": sheet.expiration.isoformat() if sheet.expiration else None
        }
        for sheet in linked_sheets
    ]


@app.put("/api/sheets/link/{file_id}/renew")
async def renew_watch_channel(
    file_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_active_user)
):
    """
    Renew watch channel for a linked Google Sheet.
    Creates a new watch channel if the current one is expired or expiring soon.
    """
    from backend import drive_service
    from datetime import datetime
    
    linked_sheet = db.query(models.LinkedSheet).filter(
        models.LinkedSheet.file_id == file_id,
        models.LinkedSheet.is_active == True
    ).first()
    
    if not linked_sheet:
        raise HTTPException(status_code=404, detail="Linked sheet not found")
    
    # Parar o canal antigo se existir
    if linked_sheet.resource_id:
        try:
            drive_service.stop_watch_channel(linked_sheet.resource_id)
        except Exception:
            # Ignorar erro se o canal já estiver expirado
            pass
    
    # Criar novo watch channel
    webhook_url = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:8001') + '/api/webhooks/google-drive'
    
    try:
        channel_info = drive_service.create_watch_channel(
            file_id=file_id,
            webhook_url=webhook_url,
            expiration_hours=168  # 7 dias
        )
        
        linked_sheet.channel_id = channel_info['channel_id']
        linked_sheet.resource_id = channel_info['resource_id']
        linked_sheet.expiration = datetime.fromtimestamp(channel_info['expiration'] / 1000)
        linked_sheet.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "renewed",
            "file_id": file_id,
            "channel_id": channel_info['channel_id'],
            "expiration": channel_info['expiration'],
            "message": "Watch channel renovado com sucesso"
        }
    except ValueError as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao renovar watch channel: {error_msg}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado ao renovar watch channel: {str(e)}"
        )


@app.get("/api/sheets/service-account-email")
async def get_service_account_email_endpoint(
    current_user = Depends(auth.get_current_active_user)
):
    """
    Get Service Account email address.
    
    This email should be shared with Google Sheets for access.
    Clients do not need to provide any API keys.
    """
    from backend import google_auth
    
    try:
        email = google_auth.get_service_account_email()
        return {
            "service_account_email": email,
            "instructions": (
                "Para vincular uma planilha do Google Sheets:\n"
                "1. Abra a planilha no Google Sheets\n"
                "2. Clique em 'Compartilhar' (botão no canto superior direito)\n"
                f"3. Adicione o email: {email}\n"
                "4. Defina a permissão como 'Visualizador'\n"
                "5. Use o endpoint /api/sheets/link com a URL da planilha"
            )
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter email do Service Account: {str(e)}"
        )


# ============ Servir Frontend React ============
# IMPORTANTE: Esta rota deve ser a ÚLTIMA, depois de todas as rotas de API

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
        port=8001,
        reload=True  # Auto-reload em desenvolvimento
    )
