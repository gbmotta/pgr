-- Schema para controle de processos administrativos (SQLite)
PRAGMA foreign_keys = ON;

-- Tipos de processo
CREATE TABLE IF NOT EXISTS process_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

-- Status possíveis
CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL
);

-- Processos principais
CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_number TEXT NOT NULL UNIQUE,
    type_id INTEGER NOT NULL REFERENCES process_types(id),
    applicant_name TEXT NOT NULL,
    applicant_registration TEXT,
    created_date TEXT NOT NULL,
    status_id INTEGER NOT NULL REFERENCES statuses(id),
    parecer TEXT,
    financial_effective_date TEXT,
    closed_date TEXT,
    notes TEXT
);

-- Catálogo de documentos
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

-- Relacionamento: documentos obrigatórios por tipo
CREATE TABLE IF NOT EXISTS required_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL REFERENCES process_types(id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    required BOOLEAN NOT NULL DEFAULT 1,
    doc_order INTEGER DEFAULT 0,
    UNIQUE(type_id, document_id)
);

-- Checklist de documentos por processo
CREATE TABLE IF NOT EXISTS process_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    required BOOLEAN NOT NULL DEFAULT 1,
    provided BOOLEAN NOT NULL DEFAULT 0,
    provided_date TEXT,
    observations TEXT,
    UNIQUE(process_id, document_id)
);

-- Prazos legais padrão
CREATE TABLE IF NOT EXISTS legal_deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER REFERENCES process_types(id),
    name TEXT NOT NULL,
    days_limit INTEGER NOT NULL,
    start_event TEXT NOT NULL,
    is_business_days BOOLEAN NOT NULL DEFAULT 0,
    description TEXT
);

-- Prazos específicos de cada processo
CREATE TABLE IF NOT EXISTS process_deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    legal_deadline_id INTEGER NOT NULL REFERENCES legal_deadlines(id),
    due_date TEXT NOT NULL,
    notified BOOLEAN NOT NULL DEFAULT 0,
    closed BOOLEAN NOT NULL DEFAULT 0,
    notes TEXT
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_process_type ON processes(type_id);
CREATE INDEX IF NOT EXISTS idx_process_status ON processes(status_id);
CREATE INDEX IF NOT EXISTS idx_pd_process ON process_documents(process_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_process ON process_deadlines(process_id);
