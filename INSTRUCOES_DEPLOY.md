# 🚀 DEPLOY RÁPIDO - 5 MINUTOS

## ✅ Código já está no GitHub!

**Repositório**: https://github.com/gbmotta/pgr

---

## 🎯 Agora faça o Deploy no Railway.app

### **Passo 1**: Criar Conta no Railway
1. Acesse: **https://railway.app**
2. Clique em **"Login with GitHub"**
3. Autorize o Railway a acessar seus repositórios

### **Passo 2**: Criar Novo Projeto
1. No painel do Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Procure e selecione: **`gbmotta/pgr`**
4. Railway detectará automaticamente que é Python ✅

### **Passo 3**: Aguardar Build
- Railway vai instalar dependências automaticamente
- Aguarde 1-2 minutos até aparecer "Success"

### **Passo 4**: Gerar Domínio Público
1. Clique no seu projeto
2. Vá em **"Settings"** (engrenagem)
3. Em **"Networking"**, clique em **"Generate Domain"**
4. ✅ URL pública será gerada! Exemplo: `pgr-production-xxxx.up.railway.app`

### **Passo 5**: Inicializar Banco de Dados

**Opção A - Via Railway CLI** (recomendado):
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Vincular ao projeto
railway link

# Executar seed
railway run python seed_sqlalchemy.py
```

**Opção B - Via Web** (alternativa):
1. No Railway, vá em **"Deployments"** → **"View Logs"**
2. Quando ver "Application startup complete"
3. Clique em **"Shell"**
4. Execute: `python seed_sqlalchemy.py`

---

## 🌐 Acessar Sistema em Produção

### Dashboard (Cliente):
```
https://seu-dominio.up.railway.app/pgr/
```

### API Docs (Swagger):
```
https://seu-dominio.up.railway.app/docs
```

### Health Check:
```
https://seu-dominio.up.railway.app/health
```

---

## 📊 Importar Dados do Cliente

Após o deploy, importe a planilha do cliente:

```bash
# Via Railway CLI
railway run python import_excel.py planilha_cliente.xlsx
```

---

## 💰 Custo

- **GRÁTIS**: $5 de crédito/mês (suficiente para uso básico)
- Se acabar: Migrar para Render.com ou Fly.io (também grátis)

---

## 🆘 Problemas?

### Erro no Build:
- Verifique os logs no Railway
- Confirme que `requirements.txt` foi enviado

### Banco de dados vazio:
- Execute: `railway run python seed_sqlalchemy.py`

### Frontend não carrega:
- Teste: `https://seu-dominio.up.railway.app/docs`
- Verifique se pasta `pgr/` foi enviada ao Git

---

## ✅ Checklist Final

- [x] Código no GitHub: https://github.com/gbmotta/pgr
- [ ] Conta criada no Railway.app
- [ ] Projeto conectado ao repositório
- [ ] Deploy concluído (verde)
- [ ] Domínio gerado
- [ ] Seed executado
- [ ] Cliente consegue acessar `/pgr/`

---

**🎯 Com isso, seu cliente pode acessar de qualquer lugar!**

Links Úteis:
- Railway: https://railway.app
- Seu Repo: https://github.com/gbmotta/pgr
- Docs Railway: https://docs.railway.app
