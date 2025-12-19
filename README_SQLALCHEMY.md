# API FastAPI com SQLAlchemy - Guia de Uso

## 📋 Visão Geral

Sistema completo de controle de processos administrativos usando **FastAPI + SQLAlchemy ORM**.

**Características:**
- ✅ FastAPI com endpoints REST completos
- ✅ SQLAlchemy ORM (Object-Relational Mapping)
- ✅ Banco de dados SQLite
- ✅ Código totalmente comentado
- ✅ Validação com Pydantic
- ✅ Relacionamentos automáticos
- ✅ Migrations-ready

## 🚀 Início Rápido

### 1. Instalar dependências

```bash
cd /home/gab/Documentos/PGR
pip install -r requirements.txt
```

### 2. Popular banco de dados

```bash
python3 seed_sqlalchemy.py
```

Isso cria:
- 2 tipos de processo (Promoção, Progressão)
- 7 status
- 7 documentos
- 4 prazos legais
- 4 processos de exemplo

### 3. Executar API

```bash
python3 api_sqlalchemy.py
```

Ou usando uvicorn diretamente:

```bash
uvicorn api_sqlalchemy:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acessar documentação

Abra no navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Endpoints Disponíveis

### Informações Gerais

```http
GET /                    # Informações da API
GET /health             # Health check (verifica banco)
GET /statistics/summary # Estatísticas gerais
```

### Processos

```http
POST   /processes                          # Cadastrar novo processo
GET    /processes                          # Listar processos (com filtros)
GET    /processes/{protocol}               # Detalhes de um processo
```

**Exemplo de cadastro:**

```bash
curl -X POST "http://localhost:8000/processes" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_number": "PGR-2025-0010",
    "type_code": "PROM_CAP",
    "applicant_name": "João da Silva",
    "applicant_registration": "123456",
    "status_code": "RECEBIDO",
    "notes": "Processo iniciado em 2025"
  }'
```

### Prazos

```http
GET /deadlines/overdue              # Listar prazos vencidos
GET /deadlines/upcoming?days=7      # Prazos próximos (próximos N dias)
```

## 🏗️ Arquitetura

### Arquivos Principais

```
PGR/
├── models_sqlalchemy.py      # Modelos ORM (tabelas)
├── api_sqlalchemy.py          # API FastAPI
├── seed_sqlalchemy.py         # Script de seed (dados iniciais)
├── requirements.txt           # Dependências Python
└── README_SQLALCHEMY.md       # Este arquivo
```

### Modelos (Tabelas)

1. **ProcessType** - Tipos de processo
2. **Status** - Status possíveis
3. **Document** - Catálogo de documentos
4. **Process** - Processos principais
5. **RequiredDocument** - Documentos obrigatórios por tipo
6. **ProcessDocument** - Checklist por processo
7. **LegalDeadline** - Prazos legais padrão
8. **ProcessDeadline** - Prazos específicos por processo

### Relacionamentos ORM

```python
# Processo → Tipo (many-to-one)
process.process_type  # Acessa o tipo do processo

# Processo → Documentos (one-to-many)
process.documents  # Lista de documentos do processo

# Processo → Prazos (one-to-many)
process.deadlines  # Lista de prazos do processo
```

## 💡 Exemplos de Uso

### Cadastrar Processo via Python

```python
from datetime import date
from models_sqlalchemy import get_engine, get_session, Process, ProcessType, Status

engine = get_engine()
db = get_session(engine)

# Buscar tipo e status
tipo = db.query(ProcessType).filter(ProcessType.code == "PROM_CAP").first()
status = db.query(Status).filter(Status.code == "RECEBIDO").first()

# Criar processo
novo_processo = Process(
    protocol_number="PGR-2025-0099",
    type_id=tipo.id,
    applicant_name="Maria Santos",
    created_date=date.today(),
    status_id=status.id
)

db.add(novo_processo)
db.commit()
```

### Listar Processos Vencidos via Python

```python
from datetime import date
from models_sqlalchemy import get_engine, get_session, ProcessDeadline, Process

engine = get_engine()
db = get_session(engine)

hoje = date.today()

vencidos = db.query(ProcessDeadline).join(Process).filter(
    ProcessDeadline.closed == False,
    ProcessDeadline.due_date < hoje
).all()

for prazo in vencidos:
    dias = (hoje - prazo.due_date).days
    print(f"Processo {prazo.process.protocol_number}: {dias} dias vencido")
```

### Buscar Processo com Relacionamentos

```python
from models_sqlalchemy import get_engine, get_session, Process

engine = get_engine()
db = get_session(engine)

# Buscar processo com relacionamentos carregados
processo = db.query(Process).filter(
    Process.protocol_number == "PGR-2025-0001"
).first()

print(f"Tipo: {processo.process_type.name}")
print(f"Status: {processo.status.label}")
print(f"Documentos: {len(processo.documents)}")
print(f"Prazos: {len(processo.deadlines)}")
```

## 🔧 Funcionalidades Implementadas

### ✅ Cadastro Automático

Ao criar um processo, o sistema automaticamente:

1. **Gera checklist de documentos** baseado no tipo
2. **Calcula e cria prazos** baseado nos prazos legais
3. **Valida** tipo de processo e status

### ✅ Cálculo de Prazos

```python
def calculate_due_date(start_date, days, business_days=False):
    """
    Calcula data de vencimento.
    - business_days=False: Dias corridos
    - business_days=True: Apenas dias úteis (seg-sex)
    """
```

### ✅ Validação com Pydantic

Todos os dados de entrada são validados:

```python
class ProcessCreateSchema(BaseModel):
    protocol_number: str  # Obrigatório
    type_code: str        # Obrigatório
    applicant_name: str   # Obrigatório
    # ... campos opcionais
```

### ✅ Dependency Injection

```python
@app.get("/processes")
def list_processes(db: Session = Depends(get_db)):
    # 'db' é injetada automaticamente
    # e fechada após a requisição
```

## 🧪 Testes

### Testar endpoint de cadastro

```bash
curl -X POST "http://localhost:8000/processes" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_number": "TEST-001",
    "type_code": "PROG_MER",
    "applicant_name": "Teste Silva"
  }'
```

### Testar endpoint de prazos vencidos

```bash
curl "http://localhost:8000/deadlines/overdue"
```

### Testar health check

```bash
curl "http://localhost:8000/health"
```

## 📊 Diferenças entre as Versões

| Recurso | api.py (SQLite direto) | api_sqlalchemy.py (ORM) |
|---------|------------------------|-------------------------|
| Queries SQL | Manuais (strings) | ORM (objetos Python) |
| Relacionamentos | Joins manuais | Automáticos |
| Validação | Manual | Pydantic schemas |
| Migrations | Não | Sim (Alembic ready) |
| Type hints | Parcial | Completo |
| Código | Mais direto | Mais abstrato |

## 🔄 Próximos Passos

### Adicionar Alembic (Migrations)

```bash
pip install alembic
alembic init alembic
```

### Adicionar Autenticação

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    # Rota protegida
```

### Adicionar Paginação

```python
@app.get("/processes")
def list_processes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(Process).offset(skip).limit(limit).all()
```

### Adicionar Filtros Avançados

```python
from sqlalchemy import or_, and_

# Busca por nome OU matrícula
processes = db.query(Process).filter(
    or_(
        Process.applicant_name.like(f"%{search}%"),
        Process.applicant_registration == search
    )
).all()
```

## 🐛 Troubleshooting

### Erro: "Import sqlalchemy could not be resolved"

```bash
pip install sqlalchemy
```

### Erro: "Table already exists"

Delete o banco e recrie:

```bash
rm PGR.db
python3 seed_sqlalchemy.py
```

### Erro: "Connection pool full"

Aumente o pool ou use connection pooling:

```python
engine = create_engine(
    "sqlite:///PGR.db",
    pool_size=10,
    max_overflow=20
)
```

## 📖 Documentação Adicional

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/

## 👤 Suporte

Para dúvidas ou problemas:
1. Verifique logs da API
2. Teste endpoints via Swagger UI (/docs)
3. Verifique se o banco foi populado corretamente

---

**Sistema pronto para uso! 🚀**
