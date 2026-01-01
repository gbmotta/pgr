# ✅ Checklist de Deploy - Sistema PGR v3.0

## 🎯 Status Atual
- ✅ Código commitado e enviado para GitHub
- ✅ Variáveis de ambiente configuradas no Railway
- ⏳ **Aguardando próximos passos...**

---

## 📋 Checklist Completo

### 1️⃣ Verificar Deploy no Railway
- [ ] Acessar: https://railway.app/project/[seu-projeto]
- [ ] Verificar se o build está rodando/sucesso
- [ ] Aguardar conclusão do build (2-5 minutos)
- [ ] Verificar logs para erros

### 2️⃣ Executar Seed do Banco de Dados
- [ ] **Opção A - Via Terminal Railway:**
  - [ ] Abrir projeto no Railway
  - [ ] Clicar em "Deployments" → Último deployment
  - [ ] Clicar em "View Logs" → "Shell" (ou "Console")
  - [ ] Executar: `cd backend && python seed_sqlalchemy.py`
  - [ ] Verificar mensagem: "✓ Seed concluído com sucesso!"

- [ ] **Opção B - Via Railway CLI:**
  ```bash
  npm install -g @railway/cli
  railway login
  railway link
  railway run python backend/seed_sqlalchemy.py
  ```

### 3️⃣ Gerar Domínio Público
- [ ] No Railway: Settings → Networking
- [ ] Clicar em "Generate Domain"
- [ ] Copiar URL gerada (ex: `pgr-production-xxxx.up.railway.app`)

### 4️⃣ Testar Sistema

#### 4.1 Testar API
- [ ] Acessar: `https://seu-dominio.up.railway.app/docs`
- [ ] Verificar Swagger UI carregou
- [ ] Testar endpoint `/health`

#### 4.2 Testar Frontend
- [ ] Acessar: `https://seu-dominio.up.railway.app`
- [ ] Verificar tela de login aparece
- [ ] Fazer login com:
  - Username: `admin`
  - Password: `admin123`
- [ ] Verificar dashboard carrega

#### 4.3 Testar Funcionalidades
- [ ] Ver lista de processos no dashboard
- [ ] Testar busca/filtros
- [ ] Testar upload de planilha Excel
- [ ] Testar visualizar detalhes de processo
- [ ] Testar gerar PDF de relatório
- [ ] Testar upload de documento anexo

### 5️⃣ Segurança (IMPORTANTE!)

- [ ] **Alterar senha do admin:**
  - Via API: POST `/api/auth/register` (criar novo usuário)
  - Ou via banco de dados direto

- [ ] **Verificar SECRET_KEY:**
  - [ ] Confirmar que é uma chave forte (32+ caracteres)
  - [ ] Não está compartilhada/publicada

- [ ] **Configurar HTTPS:**
  - [ ] Railway já fornece HTTPS automaticamente ✅

### 6️⃣ Documentação para Cliente

- [ ] Criar manual do usuário
- [ ] Documentar credenciais de acesso
- [ ] Documentar URL de acesso
- [ ] Criar guia de primeiro acesso

### 7️⃣ Monitoramento

- [ ] Configurar alertas de erro (opcional)
- [ ] Verificar logs periodicamente
- [ ] Monitorar uso de recursos no Railway

---

## 🔧 Comandos Úteis

### Verificar logs do deploy
```bash
# Via Railway CLI
railway logs
```

### Acessar shell do Railway
```bash
railway shell
```

### Fazer redeploy
```bash
# Push novo commit para GitHub
git push

# Railway fará redeploy automaticamente
```

### Resetar banco (CUIDADO!)
```bash
railway run python -c "
from backend.models_sqlalchemy import get_engine, Base
import os
os.remove('data/PGR.db')
engine = get_engine()
Base.metadata.create_all(engine)
"
# Depois executar seed novamente
railway run python backend/seed_sqlalchemy.py
```

---

## 🐛 Troubleshooting

### Build falha
- [ ] Verificar logs do Railway
- [ ] Verificar se `railway.json` está correto
- [ ] Verificar se Node.js está disponível no build

### Frontend não carrega
- [ ] Verificar se build do React foi feito
- [ ] Verificar se `frontend-dist/` existe
- [ ] Verificar logs do servidor

### Erro de autenticação
- [ ] Verificar SECRET_KEY está configurada
- [ ] Verificar banco de dados foi inicializado (seed)
- [ ] Verificar se usuário admin foi criado

### Erro ao enviar email
- [ ] Verificar variáveis SMTP
- [ ] Testar senha de app do Gmail
- [ ] Verificar logs para erro específico

---

## 📞 URLs Importantes

- **Railway Dashboard:** https://railway.app/project/[seu-projeto]
- **API Docs:** `https://seu-dominio.up.railway.app/docs`
- **Health Check:** `https://seu-dominio.up.railway.app/health`
- **Frontend:** `https://seu-dominio.up.railway.app`

---

## 🎉 Quando tudo estiver funcionando:

1. ✅ Sistema acessível publicamente
2. ✅ Login funcionando
3. ✅ Dashboard carregando processos
4. ✅ Upload de Excel funcionando
5. ✅ Geração de PDF funcionando
6. ✅ Sistema pronto para uso do cliente!

---

**Última atualização:** Dezembro 2025  
**Versão:** 3.0.0

