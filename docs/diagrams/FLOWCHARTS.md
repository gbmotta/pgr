# Fluxogramas PGR — Mermaid, diagrams e pyreverse

Este diretório concentra **três formas** de visualizar o projeto. São **6 fluxogramas PNG** (2 por ferramenta):

| # | Ferramenta | Ficheiro PNG | Origem |
|---|------------|--------------|--------|
| 1 | **diagrams** | `pgr_fluxo_geral.png` | `python3 architecture_diagrams.py` (função `build_general`) |
| 2 | **diagrams** | `pgr_fluxo_detalhado.png` | idem (`build_detailed`) |
| 3 | **Mermaid** | `mermaid_fluxo_geral.png` | `mermaid/mermaid_fluxo_geral.mmd` → `mmdc` |
| 4 | **Mermaid** | `mermaid_fluxo_detalhado.png` | `mermaid/mermaid_fluxo_detalhado.mmd` → `mmdc` |
| 5 | **pyreverse** | `pyreverse_pacotes.png` | `pyreverse_output/packages_pgr_backend.dot` → `dot -Tpng` |
| 6 | **pyreverse** | `pyreverse_classes.png` | `pyreverse_output/classes_pgr_backend.dot` → `dot -Tpng` |

Além disto: texto Mermaid embebido neste `.md`; fontes `.mmd`/`.dot` em `mermaid/` e `pyreverse_output/`.

**Regenerar os PNG Mermaid** (Node 18+; se Puppeteer falhar por sandbox Linux, usa-se `mermaid/puppeteer-config.json`):

```bash
cd docs/diagrams
npx --yes @mermaid-js/mermaid-cli@10.9.1 -p mermaid/puppeteer-config.json \
  -i mermaid/mermaid_fluxo_geral.mmd -o mermaid_fluxo_geral.png -b white -w 1200
npx --yes @mermaid-js/mermaid-cli@10.9.1 -p mermaid/puppeteer-config.json \
  -i mermaid/mermaid_fluxo_detalhado.mmd -o mermaid_fluxo_detalhado.png -b white -w 1400 -H 1600
```

---

## 1. Fluxograma geral (Mermaid)

Visão macro: utilizador, frontend, API, dados e integração opcional com Google.

```mermaid
flowchart LR
  subgraph Cliente
    U[Utilizador\nbrowser]
  end

  subgraph Frontend["Frontend (React + Vite)"]
    SPA[SPA / React Router\nTanStack Query]
  end

  subgraph Backend["Backend (FastAPI)"]
    API[api_sqlalchemy\nrotas REST]
    SVC[Serviços\nauth, ingestion, sheets,\ndrive, deadlines, audit…]
  end

  subgraph Dados["Persistência"]
    DB[(SQLite\nPGR.db)]
    FS[Pasta uploads/\nrelatórios]
  end

  subgraph Ext["Externo (opcional)"]
    G[Google Drive / Sheets\nAPI + webhooks]
  end

  U -->|HTTPS| SPA
  SPA -->|JWT + JSON\n/api /processes …| API
  API --> SVC
  SVC --> DB
  SVC --> FS
  SVC <-->|OAuth / push| G
```

---

## 2. Fluxograma detalhado (Mermaid)

### 2.1 Rotas da aplicação React

```mermaid
flowchart TB
  subgraph App["App.jsx"]
    RQ[QueryClientProvider]
    AUTH[AuthProvider]
    ROUTER[BrowserRouter]
  end

  LOGIN[/login]
  PROT["ProtectedRoute + MainLayout"]

  DASH[/dashboard]
  PERF[/performance]
  PROC["/process/:protocol"]
  UP[/upload]
  LINK[/linked-sheets]
  REP[/reports]
  CAL[/calendar]
  SET[/settings]

  ROUTER --> LOGIN
  ROUTER --> PROT
  PROT --> DASH & PERF & PROC & UP & LINK & REP & CAL & SET
```

### 2.2 Fluxo de pedido autenticado (multi-tenant)

```mermaid
flowchart TD
  A[Cliente envia pedido\nBearer JWT] --> B{Token válido?}
  B -->|não| E[401 Unauthorized]
  B -->|sim| C[Resolver utilizador\nauth]
  C --> D[Rotas /api/processes…\nfiltram por owner_user_id]
  D --> F[(SQLAlchemy Session)]
  F --> G[Resposta JSON]
```

### 2.3 Importação de processos (resumo)

```mermaid
flowchart TD
  subgraph UI["UploadProcesses.jsx"]
    M1[Modo grelha\nimport-grid]
    M2[Modo ficheiro\npreview + upload-excel]
    M3[Modo Google Drive\npreview + upload-from-google-drive]
  end

  M1 --> API1["POST /api/processes/import-grid"]
  M2 --> API2["POST preview-upload\nPOST /processes/upload-excel"]
  M3 --> API3["POST preview-google-sheets\nPOST /processes/upload-from-google-drive"]

  API1 & API2 & API3 --> ING[spreadsheet_ingestion / ingestion]
  ING --> DB[(processos na BD)]
  M3 --> SYNC{Monitorização?}
  SYNC -->|sim| LINK["POST /api/sheets/link"]
```

### 2.4 Backend: módulos que alimentam a API (visão lógica)

```mermaid
flowchart TB
  API[api_sqlalchemy.py]

  API --> AUTH[auth]
  API --> MOD[models_sqlalchemy]
  API --> ING[ingestion / spreadsheet_ingestion]
  API --> SH[sheets_service]
  API --> WH[webhook_handler / webhook_config]
  API --> DRV[drive_service / google_drive_utils]
  API --> DL[deadline_awareness]
  API --> AL[alert_service]
  API --> AU[audit_service]
  API --> AI[ai_insights]
  API --> UT[utils]

  WH --> SH
  SH --> DRV

  AUTH & ING & SH & WH & DRV & DL & AL & AU & AI --> MOD
```

### 2.5 Deploy Docker (referência)

```mermaid
flowchart LR
  subgraph VPS
    C[Caddy\nHTTPS]
    DC[Docker Compose]
    APP[PGR container\nuvicorn + frontend-dist]
    C --> APP
    DC --> APP
  end

  USER[Cliente] --> C
  APP --> VOL[(Volumes:\ndata, uploads)]
```

---

## 3. pyreverse — diagramas UML do pacote `backend`

Geração dos fontes **`.mmd`** e **`.dot`** (sem Graphviz). Para os PNG **`pyreverse_pacotes.png`** e **`pyreverse_classes.png`**, use o comando **`dot`** (pacote `graphviz` no sistema ou via conda):

```bash
cd docs/diagrams
dot -Tpng -Gdpi=120 pyreverse_output/packages_pgr_backend.dot -o pyreverse_pacotes.png
dot -Tpng -Gdpi=100 pyreverse_output/classes_pgr_backend.dot -o pyreverse_classes.png
```

Para regenerar só os fontes:

```bash
cd /path/to/PGR
mkdir -p docs/diagrams/pyreverse_output
pyreverse -o mmd -p pgr_backend backend -d docs/diagrams/pyreverse_output
pyreverse -o dot -p pgr_backend backend -d docs/diagrams/pyreverse_output
```

---

## 4. diagrams (Python) — arquitetura em PNG

**Dependências:** `pip install diagrams` e **Graphviz no sistema** (ex.: `sudo apt install graphviz` — o comando `dot` tem de existir no `PATH`).

```bash
cd docs/diagrams
pip install diagrams
python3 architecture_diagrams.py
```

Saída esperada no mesmo diretório:

- `pgr_fluxo_geral.png`
- `pgr_fluxo_detalhado.png`

Lista opcional de dependências só para diagramas: ver `requirements-diagrams.txt`.

---

## 5. Exemplo: diagrama de pacotes gerado por pyreverse

O ficheiro completo está em `pyreverse_output/packages_pgr_backend.mmd`. Segue uma cópia para pré-visualização rápida:

```mermaid
classDiagram
  class backend {
  }
  class ai_insights {
  }
  class alert_service {
  }
  class api_sqlalchemy {
  }
  class audit_service {
  }
  class auth {
  }
  class deadline_awareness {
  }
  class drive_service {
  }
  class google_auth {
  }
  class google_drive_utils {
  }
  class ingestion {
  }
  class models_sqlalchemy {
  }
  class seed_sqlalchemy {
  }
  class sheets_mapper {
  }
  class sheets_service {
  }
  class spreadsheet_ingestion {
  }
  class utils {
  }
  class webhook_config {
  }
  class webhook_handler {
  }
  api_sqlalchemy --> backend
  api_sqlalchemy --> ai_insights
  api_sqlalchemy --> alert_service
  api_sqlalchemy --> audit_service
  api_sqlalchemy --> auth
  api_sqlalchemy --> deadline_awareness
  api_sqlalchemy --> drive_service
  api_sqlalchemy --> google_auth
  api_sqlalchemy --> google_drive_utils
  api_sqlalchemy --> ingestion
  api_sqlalchemy --> sheets_service
  api_sqlalchemy --> spreadsheet_ingestion
  api_sqlalchemy --> utils
  api_sqlalchemy --> webhook_config
  api_sqlalchemy --> webhook_handler
  seed_sqlalchemy --> models_sqlalchemy
  webhook_handler --> backend
  webhook_handler --> audit_service
```
