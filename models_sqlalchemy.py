"""
Modelos SQLAlchemy para o sistema de processos administrativos.
Define as tabelas do banco de dados usando ORM.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, ForeignKey, Index, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import date

# Base para todos os modelos
Base = declarative_base()


class ProcessType(Base):
    """
    Tipos de processo disponíveis no sistema.
    Ex: Promoção por Capacitação, Progressão por Mérito
    """
    __tablename__ = 'process_types'
    
    # Colunas
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # Código único (PROM_CAP, PROG_MER)
    name = Column(String(200), nullable=False)  # Nome completo do tipo
    description = Column(Text, nullable=True)  # Descrição detalhada
    
    # Relacionamentos
    processes = relationship("Process", back_populates="process_type")
    required_documents = relationship("RequiredDocument", back_populates="process_type")
    legal_deadlines = relationship("LegalDeadline", back_populates="process_type")


class Status(Base):
    """
    Status possíveis de um processo.
    Ex: Recebido, Em Análise, Deferido, Indeferido
    """
    __tablename__ = 'statuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # Código único (RECEBIDO, DEFERIDO)
    label = Column(String(100), nullable=False)  # Rótulo exibido ao usuário
    
    # Relacionamentos
    processes = relationship("Process", back_populates="status")


class Document(Base):
    """
    Catálogo de documentos que podem ser exigidos.
    Ex: RG, CPF, Certificado de Curso
    """
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # Código único (RG, CPF)
    name = Column(String(200), nullable=False)  # Nome do documento
    description = Column(Text, nullable=True)  # Descrição/observações
    
    # Relacionamentos
    required_documents = relationship("RequiredDocument", back_populates="document")
    process_documents = relationship("ProcessDocument", back_populates="document")


class Process(Base):
    """
    Processo administrativo principal.
    Armazena todos os dados do processo de promoção/progressão.
    """
    __tablename__ = 'processes'
    
    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_number = Column(String(50), unique=True, nullable=False, index=True)  # Número de protocolo único
    type_id = Column(Integer, ForeignKey('process_types.id'), nullable=False)  # FK para tipo de processo
    applicant_name = Column(String(200), nullable=False)  # Nome do requerente
    applicant_registration = Column(String(50), nullable=True)  # Matrícula do servidor
    created_date = Column(Date, nullable=False, index=True)  # Data de criação/protocolo
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)  # FK para status atual
    
    # Campos de acompanhamento
    parecer = Column(Text, nullable=True)  # Parecer técnico/jurídico
    financial_effective_date = Column(Date, nullable=True)  # Data de efeito financeiro
    closed_date = Column(Date, nullable=True)  # Data de fechamento do processo
    notes = Column(Text, nullable=True)  # Observações gerais
    
    # Relacionamentos
    process_type = relationship("ProcessType", back_populates="processes")
    status = relationship("Status", back_populates="processes")
    documents = relationship("ProcessDocument", back_populates="process")
    deadlines = relationship("ProcessDeadline", back_populates="process")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_process_type_status', 'type_id', 'status_id'),
    )


class RequiredDocument(Base):
    """
    Documentos obrigatórios para cada tipo de processo.
    Define quais documentos devem ser apresentados.
    """
    __tablename__ = 'required_documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('process_types.id'), nullable=False)  # FK para tipo de processo
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)  # FK para documento
    required = Column(Boolean, nullable=False, default=True)  # Se é obrigatório
    doc_order = Column(Integer, default=0)  # Ordem de apresentação
    
    # Relacionamentos
    process_type = relationship("ProcessType", back_populates="required_documents")
    document = relationship("Document", back_populates="required_documents")
    
    # Índices
    __table_args__ = (
        Index('idx_req_doc_type', 'type_id'),
    )


class ProcessDocument(Base):
    """
    Checklist de documentos por processo individual.
    Controla quais documentos foram apresentados.
    """
    __tablename__ = 'process_documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    process_id = Column(Integer, ForeignKey('processes.id'), nullable=False)  # FK para processo
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)  # FK para documento
    required = Column(Boolean, nullable=False, default=True)  # Se é obrigatório neste processo
    provided = Column(Boolean, nullable=False, default=False)  # Se foi apresentado
    provided_date = Column(Date, nullable=True)  # Data de apresentação
    observations = Column(Text, nullable=True)  # Observações sobre o documento
    
    # Relacionamentos
    process = relationship("Process", back_populates="documents")
    document = relationship("Document", back_populates="process_documents")
    
    # Índices
    __table_args__ = (
        Index('idx_proc_doc_process', 'process_id'),
    )


class LegalDeadline(Base):
    """
    Prazos legais padrão por tipo de processo.
    Define os prazos que devem ser cumpridos.
    """
    __tablename__ = 'legal_deadlines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('process_types.id'), nullable=True)  # FK tipo (NULL = geral)
    name = Column(String(200), nullable=False)  # Nome do prazo
    days_limit = Column(Integer, nullable=False)  # Quantidade de dias
    start_event = Column(String(100), nullable=False)  # Evento inicial (created_date, document_complete)
    is_business_days = Column(Boolean, nullable=False, default=False)  # Se conta apenas dias úteis
    description = Column(Text, nullable=True)  # Descrição do prazo
    
    # Relacionamentos
    process_type = relationship("ProcessType", back_populates="legal_deadlines")
    process_deadlines = relationship("ProcessDeadline", back_populates="legal_deadline")


class ProcessDeadline(Base):
    """
    Prazos específicos de cada processo.
    Instâncias calculadas dos prazos legais.
    """
    __tablename__ = 'process_deadlines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    process_id = Column(Integer, ForeignKey('processes.id'), nullable=False)  # FK para processo
    legal_deadline_id = Column(Integer, ForeignKey('legal_deadlines.id'), nullable=False)  # FK prazo legal
    due_date = Column(Date, nullable=False, index=True)  # Data de vencimento calculada
    notified = Column(Boolean, nullable=False, default=False)  # Se já foi notificado
    closed = Column(Boolean, nullable=False, default=False)  # Se o prazo foi cumprido/fechado
    notes = Column(Text, nullable=True)  # Observações sobre o prazo
    
    # Relacionamentos
    process = relationship("Process", back_populates="deadlines")
    legal_deadline = relationship("LegalDeadline", back_populates="process_deadlines")
    
    # Índices
    __table_args__ = (
        Index('idx_deadline_process', 'process_id'),
        Index('idx_deadline_due', 'due_date'),
    )


# ============ Database Setup ============

def get_engine(db_path: str = "sqlite:///PGR.db"):
    """
    Cria e retorna a engine do SQLAlchemy.
    
    Args:
        db_path: String de conexão do banco (default: SQLite local)
    
    Returns:
        Engine configurada
    """
    engine = create_engine(
        db_path,
        echo=False,  # Set True para debug SQL
        future=True,
        connect_args={"check_same_thread": False}  # Necessário para SQLite
    )
    return engine


def create_tables(engine):
    """
    Cria todas as tabelas no banco de dados.
    Deve ser chamado uma vez na inicialização.
    
    Args:
        engine: Engine do SQLAlchemy
    """
    Base.metadata.create_all(engine)


def get_session(engine):
    """
    Cria e retorna uma nova sessão do banco.
    
    Args:
        engine: Engine do SQLAlchemy
    
    Returns:
        Session configurada
    """
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal()


# ============ Dependency Injection (para FastAPI) ============

def get_db():
    """
    Dependency para FastAPI que fornece uma sessão de banco.
    Garante que a sessão seja fechada após o uso.
    
    Uso:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    from sqlalchemy.orm import Session
    
    # Criar engine (em produção, use singleton)
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        yield db  # Fornece a sessão para o endpoint
    finally:
        db.close()  # Fecha a sessão após uso
