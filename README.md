# 🏛️ Sistema PGR - Processos Administrativos# PGR - Sistema de Controle de Processos Administrativos



Sistema completo de controle de processos administrativos para **Promoção por Capacitação Profissional (PROM_CAP)** e **Progressão por Mérito Profissional (PROG_MER)**.Sistema completo para gerenciamento de processos administrativos com foco em:

- **Promoção por Capacitação Profissional**

## 📋 Sumário- **Progressão por Mérito Profissional**



- [Características](#características)## Funcionalidades

- [Estrutura do Projeto](#estrutura-do-projeto)

- [Instalação](#instalação)✅ Cadastro de processos  

- [Uso](#uso)✅ Checklist de documentos obrigatórios  

- [API](#api)✅ Controle automático de prazos legais  

- [Deploy](#deploy)✅ Status padronizados  

- [Desenvolvimento](#desenvolvimento)✅ Campo de parecer e data de efeito financeiro  

✅ API REST completa  

---✅ Notificação de prazos vencidos  



## ✨ Características## Estrutura do Projeto



### Funcionalidades Principais```

PGR/

- ✅ **Cadastro de Processos**: Registro completo com protocolo, tipo, requerente├── schema.sql                  # Schema do banco de dados

- 📋 **Checklist Automático**: Documentos obrigatórios gerados automaticamente por tipo├── seed.sql                    # Dados iniciais

- ⏰ **Controle de Prazos**: Cálculo automático de prazos legais com alertas├── processes_initial.csv       # CSV inicial de processos

- 📊 **Dashboard Interativo**: Visualização em tempo real de processos e prazos├── models.py                   # Modelos de dados (Python dataclasses)

- 📤 **Upload Excel**: Importação em massa via planilha├── db_utils.py                 # Utilitários de banco de dados

- 🔍 **Busca e Filtros**: Localização rápida por protocolo, nome, status├── create_db.py               # Script de criação do banco

- 📈 **Estatísticas**: Resumo executivo com cards informativos├── api.py                      # API REST (FastAPI)

├── attach_document.py          # CLI para anexar documentos

### Tecnologias├── notify_deadlines.py         # CLI para notificar prazos vencidos

├── requirements.txt            # Dependências Python

**Backend:**├── environment.yml             # Ambiente Conda

- Python 3.11+├── tests/

- FastAPI (API REST)│   └── test_api.py            # Testes automatizados

- SQLAlchemy 2.0 (ORM)└── README.md                   # Este arquivo

- SQLite (Banco de dados)```

- Pydantic (Validação)

## Instalação

**Frontend:**

- HTML5 + CSS3### Opção 1: Conda (recomendado)

- JavaScript Vanilla

- XLSX.js (Upload Excel)```bash

cd /home/gab/Documentos/PGR

**Deploy:**conda env create -f environment.yml

- Railway.appconda activate pgr-env

- Docker ready```

- Git CI/CD

### Opção 2: pip + venv

---

```bash

## 📁 Estrutura do Projetocd /home/gab/Documentos/PGR

python3 -m venv venv

```source venv/bin/activate

PGR/pip install -r requirements.txt

├── backend/                # Backend Python```

│   ├── __init__.py

│   ├── api_sqlalchemy.py   # API REST (FastAPI)## Uso

│   ├── models_sqlalchemy.py # Modelos ORM

│   └── seed_sqlalchemy.py  # Dados iniciais### 1. Criar banco de dados

│

├── frontend/               # Frontend Web```bash

│   ├── index.html          # Dashboard principalpython3 create_db.py

│   └── upload.html         # Página de upload Excel```

│

├── scripts/                # Scripts utilitáriosIsso irá:

│   ├── import_excel.py     # Importador Excel via CLI- Criar `PGR.db` (SQLite)

│   ├── test_production.py  # Testes de produção- Aplicar schema e seeds

│   ├── test_system.py      # Testes do sistema- Importar processos do CSV

│   └── *.sh                # Scripts shell- Gerar checklists e prazos automaticamente

│

├── data/                   # Banco de dados### 2. Executar API

│   └── PGR.db              # SQLite database

│```bash

├── docs/                   # Documentaçãouvicorn api:app --reload --host 0.0.0.0 --port 8000

│   ├── README.md           # Este arquivo```

│   ├── DEPLOY_RAILWAY.md   # Guia de deploy

│   └── *.md                # Outras docsAcesse:

│- Documentação interativa: http://localhost:8000/docs

├── tests_data/             # Dados de teste- API: http://localhost:8000

│   ├── processos_teste.xlsx

│   └── template_importacao.xlsx### 3. Testes

│

├── archive/                # Código legado```bash

│pytest -v

├── requirements.txt        # Dependências Python```

├── Procfile                # Config Railway/Heroku

├── railway.json            # Config Railway### 4. Scripts CLI

└── environment.yml         # Ambiente Conda

**Anexar documento:**

``````bash

python3 attach_document.py PGR-2025-0001 CERT_CURSO 2025-12-15

---```



## 🚀 Instalação**Verificar prazos vencidos:**

```bash

### Pré-requisitospython3 notify_deadlines.py

python3 notify_deadlines.py --mark  # Marca como notificado

- Python 3.11+```

- pip ou conda

## Endpoints da API

### Passo a Passo

### Consultas

1. **Clone o repositório:**

```bash- `GET /process-types` - Lista tipos de processo

git clone https://github.com/gbmotta/pgr.git- `GET /statuses` - Lista status possíveis

cd pgr- `GET /processes` - Lista processos (com filtros)

```- `GET /processes/{protocol}` - Detalhes de um processo

- `GET /deadlines/overdue` - Prazos vencidos

2. **Crie ambiente virtual:**- `GET /deadlines/upcoming?days=7` - Prazos próximos



**Com conda:**### Operações

```bash

conda env create -f environment.yml- `POST /processes` - Criar processo

conda activate pgr-env- `PATCH /processes/{protocol}` - Atualizar processo

```- `POST /processes/{protocol}/documents/{code}/provide` - Marcar documento fornecido



**Com venv:**## Modelo de Dados

```bash

python -m venv venv### Tabelas principais:

source venv/bin/activate  # Linux/Mac

# ou- **process_types**: Tipos de processo (PROM_CAP, PROG_MER)

venv\Scripts\activate  # Windows- **statuses**: Status padronizados

```- **processes**: Processos cadastrados

- **documents**: Catálogo de documentos

3. **Instale dependências:**- **required_documents**: Documentos obrigatórios por tipo

```bash- **process_documents**: Checklist por processo

pip install -r requirements.txt- **legal_deadlines**: Prazos legais padrão

```- **process_deadlines**: Prazos específicos de cada processo



4. **Initialize o banco de dados:**## CSV Inicial

```bash

python -c "from backend.models_sqlalchemy import get_engine, create_tables; engine = get_engine(); create_tables(engine)"O arquivo `processes_initial.csv` contém exemplos de processos que são importados automaticamente. Você pode editar este arquivo antes de executar `create_db.py`.

python backend/seed_sqlalchemy.py

```Campos:

- `protocol_number`: Número do protocolo (único)

5. **Rode o servidor:**- `type_code`: PROM_CAP ou PROG_MER

```bash- `applicant_name`: Nome do requerente

uvicorn backend.api_sqlalchemy:app --reload- `applicant_registration`: Matrícula (opcional)

```- `created_date`: Data de criação (YYYY-MM-DD)

- `status_code`: Status inicial

6. **Acesse:**- `parecer`: Parecer técnico (opcional)

- Dashboard: http://localhost:8000/pgr/- `financial_effective_date`: Data de efeito financeiro (opcional)

- API Docs: http://localhost:8000/docs- `closed_date`: Data de fechamento (opcional)

- Upload: http://localhost:8000/pgr/upload.html- `notes`: Observações (opcional)



---## Próximos Passos



## 💻 UsoPara expandir o sistema, você pode:



### Via Interface Web1. **Frontend**: Criar interface web (React/Vue)

2. **Notificações por e-mail**: Integrar SMTP

#### 1. Dashboard Principal3. **Relatórios**: Gerar relatórios em PDF

Acesse `/pgr/` para visualizar:4. **Autenticação**: Adicionar login e permissões

- Cards de resumo (total, em análise, pendentes, prazos)5. **Histórico**: Log de alterações

- Lista de processos com detalhes6. **Anexos**: Upload de documentos escaneados

- Busca e filtros

- Status de documentos e prazos## Licença



#### 2. Upload de PlanilhaProjeto interno - uso institucional.

Acesse `/pgr/upload.html` para:

1. Baixar template Excel

2. Preencher dados dos processos
3. Fazer upload (drag & drop)
4. Ver prévia e validações
5. Importar em massa

### Via API

#### Criar Processo
```bash
curl -X POST http://localhost:8000/processes \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_number": "PGR-2025-0001",
    "type_code": "PROM_CAP",
    "applicant_name": "João Silva",
    "applicant_registration": "123456",
    "status_code": "RECEBIDO"
  }'
```

#### Listar Processos
```bash
curl http://localhost:8000/processes
```

#### Buscar por Protocolo
```bash
curl http://localhost:8000/processes/PGR-2025-0001
```

### Via Script Python

#### Importar Excel
```bash
# Modo teste (dry-run)
python scripts/import_excel.py arquivo.xlsx --test

# Importar de verdade
python scripts/import_excel.py arquivo.xlsx
```

---

## 📡 API

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Health check |
| `POST` | `/processes` | Criar processo |
| `GET` | `/processes` | Listar processos |
| `GET` | `/processes/{protocol}` | Detalhes do processo |
| `GET` | `/deadlines/overdue` | Prazos vencidos |
| `GET` | `/deadlines/upcoming` | Prazos próximos |
| `GET` | `/statistics/summary` | Estatísticas gerais |

### Documentação Interativa

Acesse `/docs` para Swagger UI com documentação completa e testes interativos.

---

## 🚢 Deploy

### Railway.app (Recomendado)

1. **Conecte ao GitHub:**
   - Acesse railway.app
   - New Project → Deploy from GitHub
   - Selecione o repositório `gbmotta/pgr`

2. **Configuração Automática:**
   - Railway detecta automaticamente via `Procfile`
   - Banco SQLite persistente em `/data`

3. **Acesse:**
   - URL: `https://seu-app.up.railway.app/pgr/`

Para mais detalhes, veja [docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md)

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.api_sqlalchemy:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🛠️ Desenvolvimento

### Estrutura do Código

#### Backend (Python)

**api_sqlalchemy.py** - API REST
- Endpoints FastAPI
- Validação com Pydantic
- Dependency injection para DB
- Servir frontend estático

**models_sqlalchemy.py** - ORM
- 8 tabelas relacionadas
- Modelos SQLAlchemy
- Relacionamentos (1:N, N:M)
- Índices para performance

**seed_sqlalchemy.py** - Dados Iniciais
- Tipos de processo
- Status do sistema
- Documentos padrão
- Prazos legais

#### Frontend (JavaScript)

**index.html** - Dashboard
- Carregamento assíncrono via Fetch API
- Renderização dinâmica
- Filtros e busca
- Auto-refresh (30s)

**upload.html** - Upload Excel
- XLSX.js para leitura
- Validação client-side
- Drag & drop
- Prévia de dados

### Banco de Dados

**Schema:**
```sql
process_types (tipos)
statuses (status possíveis)
documents (documentos do sistema)
processes (processos principais)
required_documents (docs obrigatórios por tipo)
process_documents (checklist por processo)
legal_deadlines (prazos legais)
process_deadlines (prazos por processo)
```

### Testes

```bash
# Testar API
python scripts/test_production.py

# Testar sistema completo
python scripts/test_system.py
```

---

## 📖 Documentação Adicional

- [DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md) - Guia completo de deploy
- [INSTRUCOES_DEPLOY.md](docs/INSTRUCOES_DEPLOY.md) - Instruções gerais
- [README_SQLALCHEMY.md](docs/README_SQLALCHEMY.md) - Detalhes técnicos do ORM

---

## 👥 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.

---

## 📧 Contato

Sistema PGR - Processos Administrativos
- Repositório: https://github.com/gbmotta/pgr
- Produção: https://web-production-41333.up.railway.app/pgr/

---

## 🎯 Roadmap

- [ ] Autenticação de usuários
- [ ] Notificações por email
- [ ] Relatórios em PDF
- [ ] Histórico de alterações
- [ ] API para integração externa
- [ ] App mobile

---

**Versão:** 2.0.0  
**Última atualização:** Dezembro 2025
