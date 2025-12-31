# 🚀 Guia de Deploy Completo - Sistema PGR v3.0

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+ e npm
- Git
- Conta Railway (para deploy em nuvem)

## 🏗️ Setup Local

### 1. Backend

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados e popular com dados iniciais
cd backend
python seed_sqlalchemy.py

# Executar API
uvicorn api_sqlalchemy:app --reload
```

A API estará disponível em: `http://localhost:8000`
Documentação Swagger: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend-react

# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

### 3. Build do Frontend

```bash
cd frontend-react
npm run build
```

Isso criará a pasta `frontend-dist` na raiz do projeto.

### 4. Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```bash
SECRET_KEY=sua-chave-secreta-min-32-caracteres
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
VITE_API_URL=http://localhost:8000
```

## 🚢 Deploy no Railway

### Opção 1: Deploy Automático via Git

1. **Conectar repositório ao Railway:**
   - Acesse [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Selecione seu repositório

2. **Configurar variáveis de ambiente:**
   - Settings → Variables
   - Adicione:
     ```
     SECRET_KEY=sua-chave-secreta-forte
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=seu-email@gmail.com
     SMTP_PASSWORD=sua-senha-app
     ```

3. **Configurar build:**
   - O `railway.json` já está configurado
   - Railway irá:
     - Instalar dependências Python
     - Buildar o frontend React
     - Iniciar o servidor FastAPI

4. **Executar seed inicial:**
   - Após o primeiro deploy, acesse o terminal do Railway
   - Execute:
     ```bash
     cd backend && python seed_sqlalchemy.py
     ```

### Opção 2: Deploy Manual

```bash
# Fazer build local do frontend
cd frontend-react
npm run build
cd ..

# Fazer commit e push
git add .
git commit -m "Build frontend para produção"
git push

# Railway fará o deploy automaticamente
```

## 🔐 Credenciais Padrão

Após executar o seed:

- **Username:** `admin`
- **Password:** `admin123`

**⚠️ IMPORTANTE:** Altere a senha do admin em produção!

## 📦 Estrutura de Deploy

```
PGR/
├── backend/
│   ├── api_sqlalchemy.py    # API principal
│   ├── models_sqlalchemy.py  # Modelos ORM
│   ├── auth.py               # Autenticação JWT
│   └── utils.py              # Utilitários (PDF, email)
├── frontend-react/           # Código fonte React
├── frontend-dist/            # Build do React (gerado)
├── data/                     # Banco SQLite
├── uploads/                  # Arquivos enviados
└── reports/                  # PDFs gerados
```

## 🔧 Comandos Úteis

### Criar novo usuário admin

```python
from backend.models_sqlalchemy import get_engine, get_session, User
from backend import auth

engine = get_engine()
db = get_session(engine)

new_admin = User(
    username="novo_admin",
    email="admin@exemplo.com",
    hashed_password=auth.get_password_hash("senha-forte"),
    full_name="Novo Admin",
    is_active=True,
    is_admin=True
)
db.add(new_admin)
db.commit()
```

### Resetar banco de dados

```bash
# Deletar banco
rm data/PGR.db

# Recriar e popular
cd backend
python seed_sqlalchemy.py
```

## 🐛 Troubleshooting

### Erro: "Module not found"

Certifique-se de que todas as dependências estão instaladas:

```bash
pip install -r requirements.txt
```

### Erro: "Frontend não encontrado"

Certifique-se de que o build foi feito:

```bash
cd frontend-react
npm run build
```

### Erro: "Cannot connect to database"

Verifique se o diretório `data/` existe e tem permissões de escrita.

### Erro no Railway: "Build failed"

1. Verifique se `railway.json` está correto
2. Verifique os logs do build no Railway
3. Certifique-se de que Node.js está instalado no ambiente

## 📝 Notas de Produção

1. **Segurança:**
   - Use SECRET_KEY forte e única
   - Habilite HTTPS
   - Configure CORS adequadamente
   - Altere credenciais padrão

2. **Banco de Dados:**
   - Para produção, considere PostgreSQL
   - Configure backups automáticos
   - Monitore tamanho do banco

3. **Uploads:**
   - Configure armazenamento em nuvem (S3, etc)
   - Limite tamanho de arquivos
   - Configure limpeza automática

4. **Email:**
   - Use serviço de email transacional (SendGrid, etc)
   - Configure SPF/DKIM
   - Monitore taxa de entrega

## 🎯 Próximos Passos

- [ ] Configurar PostgreSQL para produção
- [ ] Implementar backups automáticos
- [ ] Configurar CDN para assets
- [ ] Adicionar monitoramento (Sentry, etc)
- [ ] Configurar CI/CD completo

---

**Última atualização:** Dezembro 2025  
**Versão:** 3.0.0

