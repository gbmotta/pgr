# 🚀 Como rodar o Sistema PGR localmente

## Requisitos

- Python 3.11 ou superior
- Node.js 18+ e npm
- Git

## Instalação e Execução Rápida

Execute o script de inicialização:

```bash
./run_local.sh
```

O script vai:
1. ✅ Verificar Python e Node.js
2. ✅ Instalar dependências Python automaticamente
3. ✅ Instalar dependências Node.js automaticamente
4. ✅ Buildar o frontend React
5. ✅ Criar banco de dados inicial
6. ✅ Popular dados iniciais (usuário admin, tipos de processo, etc.)
7. ✅ Iniciar o servidor

## Acessar o Sistema

Após executar o script, acesse:

- **Aplicação:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Credenciais Padrão

- **Usuário:** `admin`
- **Senha:** `admin123`

## Instalação Manual (Alternativa)

Se preferir instalar manualmente:

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Instalar dependências Node.js e buildar frontend

```bash
cd frontend-react
npm install
npm run build
cd ..
# Copiar build para frontend-dist
cp -r frontend-react/dist frontend-dist
```

### 3. Inicializar banco de dados

```bash
python3 -c "from backend import models_sqlalchemy as models; engine = models.get_engine(); models.create_tables(engine)"
python3 -c "from backend import seed_sqlalchemy; seed_sqlalchemy.seed_database()"
```

### 4. Iniciar servidor

```bash
cd backend
python3 -m uvicorn api_sqlalchemy:app --host 0.0.0.0 --port 8000 --reload
```

## Estrutura de Diretórios

```
PGR/
├── backend/              # Backend Python/FastAPI
├── frontend-react/       # Frontend React (source)
├── frontend-dist/        # Frontend buildado (servido pelo backend)
├── data/                 # Banco de dados SQLite (PGR.db)
├── uploads/              # Arquivos enviados pelos usuários
└── reports/              # PDFs gerados
```

## Solução de Problemas

### Porta 8000 já em uso

Se a porta 8000 estiver ocupada, pare o processo ou altere a porta no `run_local.sh`:

```bash
python3 -m uvicorn api_sqlalchemy:app --host 0.0.0.0 --port 8001 --reload
```

### Erro ao importar módulos

Certifique-se de estar na raiz do projeto ao executar os comandos.

### Frontend não aparece

Execute manualmente o build do frontend:

```bash
cd frontend-react
npm run build
cd ..
cp -r frontend-react/dist frontend-dist
```

