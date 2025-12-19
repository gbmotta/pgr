"""
API REST para controle de processos administrativos.
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from db_utils import get_conn, compute_due_date

app = FastAPI(
    title="PGR - Sistema de Processos",
    description="API para controle de processos administrativos e prazos",
    version="1.0.0"
)

# ============ Schemas Pydantic ============

class ProcessCreate(BaseModel):
    protocol_number: str
    type_code: str
    applicant_name: str
    applicant_registration: Optional[str] = None
    created_date: Optional[str] = None
    status_code: str = "RECEBIDO"
    notes: Optional[str] = None

class ProcessUpdate(BaseModel):
    status_code: Optional[str] = None
    parecer: Optional[str] = None
    financial_effective_date: Optional[str] = None
    closed_date: Optional[str] = None
    notes: Optional[str] = None

class DocumentProvide(BaseModel):
    provided_date: Optional[str] = None
    observations: Optional[str] = None

# ============ Endpoints ============

@app.get("/")
def root():
    return {"message": "PGR API - Sistema de Processos Administrativos"}

@app.get("/process-types")
def list_process_types():
    """Lista tipos de processo disponíveis."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT code, name, description FROM process_types ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.get("/statuses")
def list_statuses():
    """Lista status possíveis."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT code, label FROM statuses ORDER BY label")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.get("/processes")
def list_processes(
    type_code: Optional[str] = Query(None),
    status_code: Optional[str] = Query(None)
):
    """Lista processos com filtros opcionais."""
    conn = get_conn()
    cur = conn.cursor()
    
    query = """
        SELECT p.protocol_number, pt.code AS type_code, pt.name AS type_name,
               p.applicant_name, p.applicant_registration,
               p.created_date, s.code AS status_code, s.label AS status_label,
               p.financial_effective_date
        FROM processes p
        JOIN process_types pt ON pt.id = p.type_id
        JOIN statuses s ON s.id = p.status_id
        WHERE 1=1
    """
    params = []
    
    if type_code:
        query += " AND pt.code = ?"
        params.append(type_code)
    if status_code:
        query += " AND s.code = ?"
        params.append(status_code)
    
    query += " ORDER BY p.created_date DESC"
    
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.get("/processes/{protocol}")
def get_process(protocol: str):
    """Detalhes completos de um processo incluindo checklist e prazos."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Dados do processo
    cur.execute("""
        SELECT p.*, pt.code AS type_code, pt.name AS type_name,
               s.code AS status_code, s.label AS status_label
        FROM processes p
        JOIN process_types pt ON pt.id = p.type_id
        JOIN statuses s ON s.id = p.status_id
        WHERE p.protocol_number = ?
    """, (protocol,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    proc = dict(row)
    
    # Checklist de documentos
    cur.execute("""
        SELECT d.code AS document_code, d.name AS document_name,
               pd.required, pd.provided, pd.provided_date, pd.observations
        FROM process_documents pd
        JOIN documents d ON d.id = pd.document_id
        WHERE pd.process_id = ?
        ORDER BY pd.id
    """, (proc['id'],))
    proc['documents'] = [dict(r) for r in cur.fetchall()]
    
    # Prazos
    cur.execute("""
        SELECT ld.name AS deadline_name, pdl.due_date,
               pdl.notified, pdl.closed, pdl.notes
        FROM process_deadlines pdl
        JOIN legal_deadlines ld ON ld.id = pdl.legal_deadline_id
        WHERE pdl.process_id = ?
        ORDER BY pdl.due_date
    """, (proc['id'],))
    proc['deadlines'] = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return proc

@app.post("/processes", status_code=201)
def create_process(payload: ProcessCreate):
    """Cria novo processo e gera checklist/prazos automaticamente."""
    created_date = payload.created_date or date.today().isoformat()
    
    conn = get_conn()
    cur = conn.cursor()
    
    # Validar tipo e status
    cur.execute("SELECT id FROM process_types WHERE code = ?", (payload.type_code,))
    type_row = cur.fetchone()
    if not type_row:
        conn.close()
        raise HTTPException(status_code=400, detail="Tipo de processo inválido")
    type_id = type_row['id']
    
    cur.execute("SELECT id FROM statuses WHERE code = ?", (payload.status_code,))
    status_row = cur.fetchone()
    if not status_row:
        conn.close()
        raise HTTPException(status_code=400, detail="Status inválido")
    status_id = status_row['id']
    
    # Inserir processo
    try:
        cur.execute("""
            INSERT INTO processes
            (protocol_number, type_id, applicant_name, applicant_registration,
             created_date, status_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.protocol_number,
            type_id,
            payload.applicant_name,
            payload.applicant_registration,
            created_date,
            status_id,
            payload.notes
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Erro ao criar processo: {str(e)}")
    
    # Buscar ID do processo criado
    cur.execute("SELECT id FROM processes WHERE protocol_number = ?", (payload.protocol_number,))
    proc_id = cur.fetchone()['id']
    
    # Gerar checklist
    cur.execute("""
        SELECT document_id, required
        FROM required_documents
        WHERE type_id = ?
        ORDER BY doc_order
    """, (type_id,))
    for doc_row in cur.fetchall():
        cur.execute("""
            INSERT INTO process_documents
            (process_id, document_id, required, provided)
            VALUES (?, ?, ?, 0)
        """, (proc_id, doc_row['document_id'], doc_row['required']))
    
    # Gerar prazos
    cur.execute("""
        SELECT id, days_limit, start_event, is_business_days
        FROM legal_deadlines
        WHERE type_id IS NULL OR type_id = ?
    """, (type_id,))
    for ld in cur.fetchall():
        if ld['start_event'] != 'created_date':
            continue
        due = compute_due_date(created_date, ld['days_limit'], ld['is_business_days'])
        cur.execute("""
            INSERT INTO process_deadlines
            (process_id, legal_deadline_id, due_date)
            VALUES (?, ?, ?)
        """, (proc_id, ld['id'], due))
    
    conn.commit()
    conn.close()
    
    return {"protocol_number": payload.protocol_number, "status": "created"}

@app.patch("/processes/{protocol}")
def update_process(protocol: str, payload: ProcessUpdate):
    """Atualiza dados do processo (status, parecer, datas)."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Verificar se processo existe
    cur.execute("SELECT id FROM processes WHERE protocol_number = ?", (protocol,))
    proc = cur.fetchone()
    if not proc:
        conn.close()
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    updates = []
    params = []
    
    if payload.status_code:
        cur.execute("SELECT id FROM statuses WHERE code = ?", (payload.status_code,))
        status_row = cur.fetchone()
        if not status_row:
            conn.close()
            raise HTTPException(status_code=400, detail="Status inválido")
        updates.append("status_id = ?")
        params.append(status_row['id'])
    
    if payload.parecer is not None:
        updates.append("parecer = ?")
        params.append(payload.parecer)
    
    if payload.financial_effective_date is not None:
        updates.append("financial_effective_date = ?")
        params.append(payload.financial_effective_date)
    
    if payload.closed_date is not None:
        updates.append("closed_date = ?")
        params.append(payload.closed_date)
    
    if payload.notes is not None:
        updates.append("notes = ?")
        params.append(payload.notes)
    
    if not updates:
        conn.close()
        return {"message": "Nenhuma atualização fornecida"}
    
    query = f"UPDATE processes SET {', '.join(updates)} WHERE protocol_number = ?"
    params.append(protocol)
    
    cur.execute(query, params)
    conn.commit()
    conn.close()
    
    return {"protocol_number": protocol, "status": "updated"}

@app.post("/processes/{protocol}/documents/{document_code}/provide")
def provide_document(protocol: str, document_code: str, payload: DocumentProvide):
    """Marca documento como fornecido."""
    provided_date = payload.provided_date or date.today().isoformat()
    
    conn = get_conn()
    cur = conn.cursor()
    
    # Buscar processo
    cur.execute("SELECT id, type_id FROM processes WHERE protocol_number = ?", (protocol,))
    proc = cur.fetchone()
    if not proc:
        conn.close()
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Buscar documento
    cur.execute("SELECT id FROM documents WHERE code = ?", (document_code,))
    doc = cur.fetchone()
    if not doc:
        conn.close()
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    # Atualizar checklist
    cur.execute("""
        UPDATE process_documents
        SET provided = 1, provided_date = ?, observations = ?
        WHERE process_id = ? AND document_id = ?
    """, (provided_date, payload.observations, proc['id'], doc['id']))
    
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item de checklist não encontrado")
    
    conn.commit()
    
    # Verificar se todos documentos obrigatórios foram fornecidos
    cur.execute("""
        SELECT COUNT(*) AS missing
        FROM process_documents
        WHERE process_id = ? AND required = 1 AND provided = 0
    """, (proc['id'],))
    
    missing = cur.fetchone()['missing']
    
    # Se completo, gerar prazos com start_event='document_complete'
    if missing == 0:
        cur.execute("""
            SELECT MAX(provided_date) AS last_date
            FROM process_documents
            WHERE process_id = ? AND required = 1
        """, (proc['id'],))
        last_date = cur.fetchone()['last_date']
        
        cur.execute("""
            SELECT id, days_limit, is_business_days
            FROM legal_deadlines
            WHERE (type_id IS NULL OR type_id = ?) AND start_event = 'document_complete'
        """, (proc['type_id'],))
        
        for ld in cur.fetchall():
            due = compute_due_date(last_date, ld['days_limit'], ld['is_business_days'])
            cur.execute("""
                INSERT OR IGNORE INTO process_deadlines
                (process_id, legal_deadline_id, due_date)
                VALUES (?, ?, ?)
            """, (proc['id'], ld['id'], due))
        
        conn.commit()
    
    conn.close()
    return {
        "protocol_number": protocol,
        "document_code": document_code,
        "provided_date": provided_date,
        "all_provided": missing == 0
    }

@app.get("/deadlines/overdue")
def list_overdue_deadlines():
    """Lista prazos vencidos (não fechados)."""
    conn = get_conn()
    cur = conn.cursor()
    today = date.today().isoformat()
    
    cur.execute("""
        SELECT p.protocol_number, pt.code AS type_code, pt.name AS type_name,
               ld.name AS deadline_name, pdl.due_date,
               julianday(?) - julianday(pdl.due_date) AS days_overdue
        FROM process_deadlines pdl
        JOIN processes p ON p.id = pdl.process_id
        JOIN process_types pt ON pt.id = p.type_id
        JOIN legal_deadlines ld ON ld.id = pdl.legal_deadline_id
        WHERE pdl.closed = 0 AND pdl.due_date < ?
        ORDER BY pdl.due_date ASC
    """, (today, today))
    
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r['days_overdue'] = int(round(r['days_overdue']))
    
    conn.close()
    return rows

@app.get("/deadlines/upcoming")
def list_upcoming_deadlines(days: int = Query(7, ge=1, le=90)):
    """Lista prazos próximos (nos próximos N dias)."""
    conn = get_conn()
    cur = conn.cursor()
    today = date.today()
    end_date = (today + datetime.timedelta(days=days)).isoformat()
    
    cur.execute("""
        SELECT p.protocol_number, pt.code AS type_code, pt.name AS type_name,
               ld.name AS deadline_name, pdl.due_date,
               julianday(pdl.due_date) - julianday(?) AS days_remaining
        FROM process_deadlines pdl
        JOIN processes p ON p.id = pdl.process_id
        JOIN process_types pt ON pt.id = p.type_id
        JOIN legal_deadlines ld ON ld.id = pdl.legal_deadline_id
        WHERE pdl.closed = 0 AND pdl.due_date >= ? AND pdl.due_date <= ?
        ORDER BY pdl.due_date ASC
    """, (today.isoformat(), today.isoformat(), end_date))
    
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r['days_remaining'] = int(round(r['days_remaining']))
    
    conn.close()
    return rows
