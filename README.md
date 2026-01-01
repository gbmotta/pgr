# 🏛️ Sistema PGR - Processos Administrativos

Sistema completo para gerenciamento de processos administrativos com foco em:
- **Promoção por Capacitação Profissional (PROM_CAP)**
- **Progressão por Mérito Profissional (PROG_MER)**

## ✨ Funcionalidades

- ✅ **Cadastro de Processos** - Registro completo com protocolo, tipo, requerente
- 📋 **Checklist Automático** - Documentos obrigatórios gerados automaticamente por tipo
- ⏰ **Controle de Prazos** - Cálculo automático de prazos legais com alertas
- 📊 **Dashboard Interativo** - Visualização em tempo real (React)
- 📤 **Upload Excel** - Importação em massa via planilha
- 🔍 **Busca e Filtros** - Localização rápida por protocolo, nome, status
- 📈 **Estatísticas** - Resumo executivo com cards informativos
- 🔐 **Autenticação JWT** - Sistema de login seguro
- 📄 **Geração de PDF** - Relatórios automáticos
- 📧 **Notificações** - Email para prazos vencidos

## 🛠️ Tecnologias

**Backend:**
- Python 3.11+
- FastAPI (API REST)
- SQLAlchemy 2.0 (ORM)
- SQLite/PostgreSQL (Banco de dados)
- Pydantic (Validação)

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Query
- Axios

**Deploy:**
- Railway.app
- Nixpacks

## 📁 Estrutura do Projeto

```
PGR/
├── backend/                  # Backend Python
│   ├── api_sqlalchemy.py    # API REST (FastAPI)
│   ├── models_sqlalchemy.py # Modelos ORM
│   ├── seed_sqlalchemy.py   # Dados iniciais
│   ├── auth.py              # Autenticação JWT
│   └── utils.py             # Utilitários (PDF, email)
│
├── frontend-react/          # Frontend React
│   ├── src/
│   │   ├── pages/          # Páginas principais
│   │   ├── components/     # Componentes reutilizáveis
│   │   └── contexts/       # Context API (auth)
│   └── package.json
│
├── scripts/                 # Scripts utilitários
│   ├── import_excel.py     # Importador Excel via CLI
│   ├── check_deadlines.py  # Verificar prazos
│   └── notify_deadlines.py # Notificar prazos
│
├── docs/                   # Documentação
│   ├── DEPLOY_COMPLETO.md  # Guia de deploy
│   ├── ESTRATEGIA_PRECIFICACAO.md
│   └── CONFIGURAR_GMAIL_SMTP.md
│
├── data/                   # Banco de dados (SQLite)
├── uploads/                # Arquivos enviados
├── reports/                # PDFs gerados
│
├── requirements.txt        # Dependências Python
├── Procfile               # Config Railway
├── nixpacks.toml          # Build config
├── build.sh               # Script de build
└── README.md              # Este arquivo
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Node.js 18+ e npm
- Git

### Setup Local

1. **Clone o repositório:**
```bash
git clone https://github.com/gbmotta/pgr.git
cd pgr
```

2. **Backend:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados e popular com dados iniciais
cd backend
python seed_sqlalchemy.py

# Executar API
python -m uvicorn api_sqlalchemy:app --reload
```

API disponível em: `http://localhost:8000`  
Documentação: `http://localhost:8000/docs`

3. **Frontend:**
```bash
cd frontend-react

# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

Frontend disponível em: `http://localhost:3000`

4. **Build do Frontend (para produção):**
```bash
cd frontend-react
npm run build
```

Isso criará a pasta `frontend-dist` na raiz.

## 📡 API

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/api/auth/login` | Login |
| `GET` | `/api/auth/me` | Usuário atual |
| `POST` | `/processes` | Criar processo |
| `GET` | `/processes` | Listar processos |
| `GET` | `/processes/{protocol}` | Detalhes do processo |
| `POST` | `/processes/upload-excel` | Upload Excel |
| `GET` | `/deadlines/overdue` | Prazos vencidos |
| `GET` | `/statistics/summary` | Estatísticas |

Documentação interativa: `/docs`

## 🔐 Credenciais Padrão

Após executar o seed:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **IMPORTANTE:** Altere estas credenciais em produção!

## 🚢 Deploy

### Railway.app (Recomendado)

1. **Conecte ao GitHub:**
   - Acesse [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Selecione o repositório

2. **Configuração:**
   - Railway detecta automaticamente via `Procfile` e `nixpacks.toml`
   - Build automático via `build.sh`
   - Banco SQLite persistente

3. **Inicializar Banco:**
   - No Railway → Shell do deployment
   - Execute: `cd backend && python seed_sqlalchemy.py`

4. **Acesse:**
   - URL: `https://seu-app.up.railway.app/`
   - Login: `admin` / `admin123`

Para mais detalhes, veja [docs/DEPLOY_COMPLETO.md](docs/DEPLOY_COMPLETO.md)

## 💻 Scripts CLI

### Importar Excel
```bash
python scripts/import_excel.py arquivo.xlsx
```

### Verificar Prazos
```bash
python scripts/check_deadlines.py
```

### Notificar Prazos
```bash
python scripts/notify_deadlines.py
```

## 📖 Documentação

- [Guia de Deploy](docs/DEPLOY_COMPLETO.md) - Instruções completas de deploy
- [Guia de Teste](GUIA_TESTE_CLIENTE.md) - Como testar como cliente
- [Configurar Email](docs/CONFIGURAR_GMAIL_SMTP.md) - Setup SMTP para notificações
- [Estratégia de Precificação](docs/ESTRATEGIA_PRECIFICACAO.md) - Documentação de negócio

## 🗄️ Modelo de Dados

### Tabelas Principais

- **process_types** - Tipos de processo (PROM_CAP, PROG_MER)
- **statuses** - Status padronizados
- **processes** - Processos cadastrados
- **documents** - Catálogo de documentos
- **required_documents** - Documentos obrigatórios por tipo
- **process_documents** - Checklist por processo
- **legal_deadlines** - Prazos legais padrão
- **process_deadlines** - Prazos específicos de cada processo
- **users** - Usuários do sistema
- **document_attachments** - Anexos de documentos

## 🔄 Próximos Passos

- [ ] Migração para PostgreSQL
- [ ] Notificações por email automáticas
- [ ] Histórico de alterações
- [ ] API para integração externa
- [ ] Dashboard de analytics

## 📄 Licença

Projeto interno - uso institucional.

## 📧 Contato

- Repositório: https://github.com/gbmotta/pgr
- Produção: https://web-production-41333.up.railway.app/

---

**Versão:** 3.0.0  
**Última atualização:** Janeiro 2026
