# 🚀 Deploy no Railway.app - Sistema PGR

Este guia mostra como colocar o sistema em produção **gratuitamente** usando Railway.app.

## 📋 Pré-requisitos

- Conta no GitHub (para versionar o código)
- Conta no Railway.app (grátis: https://railway.app)
- Git instalado na máquina

---

## 🎯 Passo a Passo Completo

### 1️⃣ **Preparar o Projeto para Deploy**

Já criamos todos os arquivos necessários! ✅

Arquivos importantes:
- ✅ `requirements.txt` - Dependências Python
- ✅ `api_sqlalchemy.py` - API FastAPI
- ✅ `models_sqlalchemy.py` - Modelos do banco
- ✅ `seed_sqlalchemy.py` - Dados iniciais
- ⏳ `Procfile` - Comando para iniciar (vamos criar)
- ⏳ `railway.json` - Configuração Railway (vamos criar)

### 2️⃣ **Criar Procfile**

```bash
# Este arquivo já será criado automaticamente
# Conteúdo: web: uvicorn api_sqlalchemy:app --host 0.0.0.0 --port $PORT
```

### 3️⃣ **Criar Repositório Git**

```bash
cd /home/gab/Documentos/PGR

# Inicializar Git (se ainda não foi feito)
git init

# Adicionar arquivos
git add api_sqlalchemy.py models_sqlalchemy.py seed_sqlalchemy.py
git add requirements.txt Procfile railway.json
git add pgr/  # Frontend
git add import_excel.py  # Importador

# Ignorar arquivos desnecessários
echo "PGR.db" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.xlsx" >> .gitignore
echo ".env" >> .gitignore

git add .gitignore

# Commit inicial
git commit -m "Sistema PGR completo - pronto para deploy"
```

### 4️⃣ **Criar Repositório no GitHub**

1. Acesse: https://github.com/new
2. Nome: `pgr-sistema` (ou outro nome)
3. Descrição: `Sistema de Controle de Processos Administrativos`
4. Público ou Privado (sua escolha)
5. **NÃO** adicione README, .gitignore ou licença
6. Clique em **Create repository**

7. Conectar repositório local ao GitHub:
```bash
git remote add origin https://github.com/SEU_USUARIO/pgr-sistema.git
git branch -M main
git push -u origin main
```

### 5️⃣ **Deploy no Railway**

#### A. Criar Conta
1. Acesse: https://railway.app
2. Clique em **"Login with GitHub"**
3. Autorize o Railway a acessar seus repositórios

#### B. Criar Novo Projeto
1. Clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório `pgr-sistema`
4. Railway detectará automaticamente que é Python

#### C. Configurar Variáveis de Ambiente
1. Clique na aba **"Variables"**
2. Adicione:
   - `PYTHON_VERSION` = `3.11`
   - `PORT` = `8000` (Railway define automaticamente)

#### D. Inicializar Banco de Dados
1. Após o primeiro deploy, clique em **"View Logs"**
2. Quando aparecer "Application startup complete", execute:
```bash
# No terminal Railway ou localmente com Railway CLI
railway run python seed_sqlalchemy.py
```

### 6️⃣ **Obter URL Pública**

1. Na página do projeto, clique em **"Settings"**
2. Em **"Networking"**, clique em **"Generate Domain"**
3. Você receberá uma URL tipo: `https://pgr-sistema-production.up.railway.app`

🎉 **Pronto! Sistema no ar!**

---

## 🌐 Acessar o Sistema

### Frontend (Cliente)
```
https://seu-app.up.railway.app/pgr/
```

### API (Documentação)
```
https://seu-app.up.railway.app/docs
```

### Endpoints
```
POST   https://seu-app.up.railway.app/processes
GET    https://seu-app.up.railway.app/processes
GET    https://seu-app.up.railway.app/processes/{protocol}
GET    https://seu-app.up.railway.app/deadlines/overdue
GET    https://seu-app.up.railway.app/statistics/summary
```

---

## 📊 Importar Dados Existentes do Excel

### Opção 1: Via Railway CLI (recomendado)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Fazer login
railway login

# Vincular ao projeto
railway link

# Importar Excel
railway run python import_excel.py planilha_cliente.xlsx
```

### Opção 2: Via API (remotamente)

Você pode criar um script que leia o Excel e envie via API:

```python
import pandas as pd
import requests

API_URL = "https://seu-app.up.railway.app"

# Ler Excel
df = pd.read_excel("planilha_cliente.xlsx")

# Para cada linha, fazer POST
for idx, row in df.iterrows():
    data = {
        "protocol_number": row['Protocolo'],
        "type_code": row['Tipo'],
        "applicant_name": row['Requerente'],
        "applicant_registration": row['Matrícula'],
        "created_date": row['Data'].strftime('%Y-%m-%d')
    }
    
    response = requests.post(f"{API_URL}/processes", json=data)
    print(f"✅ {row['Protocolo']}: {response.status_code}")
```

---

## 🔄 Atualizar Sistema (após mudanças)

```bash
# Fazer alterações no código local
# ...

# Commit
git add .
git commit -m "Descrição das mudanças"

# Push para GitHub
git push origin main

# Railway faz deploy automático! 🚀
```

---

## 💰 Limites do Plano Gratuito

Railway oferece:
- ✅ $5 de crédito grátis/mês (suficiente para projetos pequenos)
- ✅ Deploy automático via Git
- ✅ HTTPS incluído
- ✅ Domínio customizado (adicionar seu próprio domínio)
- ✅ Logs em tempo real
- ✅ Backups automáticos

Se acabar o crédito mensal:
1. **Render.com** - Alternativa gratuita
2. **Fly.io** - Outra opção grátis
3. **PythonAnywhere** - Específico para Python

---

## 🆘 Troubleshooting

### Erro: "Application failed to start"
- Verifique os logs no Railway
- Confirme que `requirements.txt` tem todas as dependências
- Certifique-se que `Procfile` está correto

### Erro: "Database not found"
- Execute: `railway run python seed_sqlalchemy.py`

### Frontend não carrega
- Verifique se a pasta `pgr/` foi enviada ao Git
- Confirme que `app.mount("/pgr", ...)` está no código

### Processos não aparecem
- Acesse `/docs` e teste os endpoints manualmente
- Verifique se o seed foi executado

---

## 📞 Suporte

- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- GitHub Issues: Crie issues no seu repositório

---

## ✅ Checklist Final

Antes do deploy, certifique-se:

- [ ] `requirements.txt` completo
- [ ] `Procfile` criado
- [ ] `railway.json` criado
- [ ] Frontend (`pgr/index.html`) incluído
- [ ] Git commit de tudo
- [ ] Push para GitHub
- [ ] Projeto criado no Railway
- [ ] Domínio gerado
- [ ] Seed executado
- [ ] Testes nos endpoints
- [ ] Cliente consegue acessar frontend

---

## 🎯 Próximos Passos

1. **Domínio Customizado**: `www.processos.empresa.com.br`
2. **Autenticação**: Adicionar login de usuários
3. **Relatórios PDF**: Gerar relatórios automáticos
4. **Notificações Email**: Avisar sobre prazos vencidos
5. **Backup Automático**: Exportar banco diariamente

---

**🚀 Sucesso no deploy!**

Qualquer dúvida, consulte a documentação oficial do Railway ou entre em contato.
