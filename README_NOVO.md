# 🏛️ Sistema PGR - Controle de Processos Administrativos

Sistema completo para gestão de processos de **Promoção por Capacitação Profissional (PROM_CAP)** e **Progressão por Mérito Profissional (PROG_MER)** com interface web, API REST e importador de Excel.

![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)

---

## ✨ Funcionalidades

- ✅ **Cadastro Completo** - Registro de processos com todos os dados
- ✅ **Checklist Automático** - Documentos obrigatórios gerados por tipo de processo
- ✅ **Controle de Prazos** - Deadlines legais com cálculo automático (dias úteis)
- ✅ **Status Padronizados** - 7 status (Recebido → Deferido/Indeferido)
- ✅ **Dashboard Web** - Interface visual moderna e responsiva
- ✅ **Importação Excel** - Migre sua planilha existente com 1 comando
- ✅ **API REST** - 10+ endpoints documentados automaticamente
- ✅ **Notificações** - Alerta de prazos vencidos e próximos do vencimento
- ✅ **Busca Inteligente** - Filtro por protocolo, nome, matrícula ou status
- ✅ **Estatísticas** - Resumo executivo do sistema

---

## 📸 Screenshots

### Dashboard Principal
```
🎯 Interface mostra:
- Cards coloridos por status
- Checklist de documentos (✓ entregue / ✗ pendente)
- Prazos com contador regressivo
- Busca em tempo real
```

### Importador Excel
```
📊 Detecção automática de colunas
✅ Validação antes de importar
🔄 Processamento em lote
```

---

## 🚀 Início Rápido (5 minutos)

### 1️⃣ Instalar Dependências

```bash
# Ativar ambiente conda
conda activate pgr-env

# Instalar pacotes
pip install -r requirements.txt
```

### 2️⃣ Criar Banco de Dados

```bash
python seed_sqlalchemy.py
```

Saída esperada:
```
✅ Tipos de processo criados: PROM_CAP, PROG_MER
✅ 7 status criados
✅ 7 documentos criados
✅ 4 prazos legais configurados
✅ 4 processos de exemplo criados
```

### 3️⃣ Iniciar Servidor

```bash
uvicorn api_sqlalchemy:app --reload --host 0.0.0.0 --port 8000
```

### 4️⃣ Acessar Sistema

| Interface | URL | Descrição |
|-----------|-----|-----------|
| **Dashboard** | http://localhost:8000/pgr/ | Interface para cliente |
| **API Docs** | http://localhost:8000/docs | Swagger interativo |
| **Health** | http://localhost:8000/health | Status do sistema |

---

## 📊 Importar Planilha Excel do Cliente

### Passo 1: Criar Template (ou usar planilha existente)

```bash
python import_excel.py --template
```

Cria `template_importacao.xlsx` com colunas de exemplo.

### Passo 2: Testar Importação (sem salvar)

```bash
python import_excel.py planilha_cliente.xlsx --test
```

Saída mostra o que será importado:
```
✓ PGR-2025-0020 - João Silva (PROM_CAP) [RECEBIDO]
✓ PGR-2025-0021 - Maria Santos (PROG_MER) [EM_ANALISE]

🔍 MODO DE TESTE (nada foi salvo)
   ✓ 2 processos seriam importados
```

### Passo 3: Importar de Verdade

```bash
python import_excel.py planilha_cliente.xlsx
```

```
✅ PGR-2025-0020 - João Silva (ID: 6)
✅ PGR-2025-0021 - Maria Santos (ID: 7)

✅ IMPORTAÇÃO CONCLUÍDA!
   ✓ 2 processos importados
```

### Formato do Excel

O importador detecta automaticamente colunas com estes nomes:

| Obrigatório | Nome da Coluna | Exemplos Aceitos | Formato |
|-------------|----------------|------------------|---------|
| ✅ | Protocolo | "Protocolo", "Número", "Processo" | PGR-2025-0001 |
| ✅ | Tipo | "Tipo", "Modalidade" | PROM_CAP ou PROG_MER |
| ✅ | Requerente | "Requerente", "Servidor", "Nome" | Nome completo |
| ⬜ | Matrícula | "Matrícula", "SIAPE" | 123456 |
| ⬜ | Status | "Status", "Situação" | RECEBIDO, EM_ANALISE, etc |
| ⬜ | Data | "Data", "Data Abertura" | 19/12/2025 |
| ⬜ | Efeito Financeiro | "Efeito Financeiro" | 01/01/2026 |
| ⬜ | Parecer | "Parecer", "Observação" | Texto livre |

**📌 Dica**: Não precisa renomear todas as colunas! O sistema detecta variações.

---

## 📡 API REST - Principais Endpoints

### Criar Processo

```bash
curl -X POST http://localhost:8000/processes \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_number": "PGR-2025-0100",
    "type_code": "PROM_CAP",
    "applicant_name": "Maria Silva",
    "applicant_registration": "123456",
    "created_date": "2025-12-19"
  }'
```

**Resposta**: Processo criado + checklist de 4 documentos + 3 prazos calculados automaticamente

### Listar Todos os Processos

```bash
curl http://localhost:8000/processes
```

### Buscar por Protocolo

```bash
curl http://localhost:8000/processes/PGR-2025-0100
```

**Retorna**: Dados completos + documentos + prazos

### Processos com Prazos Vencidos

```bash
curl http://localhost:8000/deadlines/overdue
```

### Prazos Próximos do Vencimento

```bash
curl "http://localhost:8000/deadlines/upcoming?days=7"
```

### Estatísticas do Sistema

```bash
curl http://localhost:8000/statistics/summary
```

```json
{
  "total_processes": 8,
  "by_status": {
    "RECEBIDO": 3,
    "EM_ANALISE": 2,
    "DEFERIDO": 2,
    "PENDENTE_DOCS": 1
  },
  "overdue_deadlines": 0
}
```

---

## 🌐 Deploy em Produção (Railway.app)

### Guia Completo de Deploy

Veja o arquivo **[DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)** com instruções passo a passo.

**Resumo**:
1. Criar repositório Git
2. Push para GitHub
3. Conectar Railway ao repositório
4. Deploy automático em 2 minutos
5. URL pública gerada: `https://seu-app.up.railway.app`

**Custo**: Grátis ($5 crédito/mês incluso)

---

## 📁 Estrutura do Projeto

```
PGR/
├── 🎨 Frontend
│   └── pgr/
│       └── index.html              # Dashboard web
│
├── 🔧 Backend
│   ├── api_sqlalchemy.py           # API FastAPI (10+ endpoints)
│   ├── models_sqlalchemy.py        # Modelos SQLAlchemy
│   └── seed_sqlalchemy.py          # Dados iniciais
│
├── 📊 Importação
│   ├── import_excel.py             # Importador Excel
│   └── template_importacao.xlsx    # Template de exemplo
│
├── 🚀 Deploy
│   ├── Procfile                    # Comando Railway/Heroku
│   ├── railway.json                # Config Railway
│   ├── requirements.txt            # Dependências
│   └── .gitignore                  # Arquivos ignorados
│
└── 📖 Documentação
    ├── README.md                   # Este arquivo
    ├── DEPLOY_RAILWAY.md           # Guia de deploy
    └── README_SQLALCHEMY.md        # Docs técnicas
```

---

## 🗄️ Modelo de Dados

### Tipos de Processo
- `PROM_CAP` - Promoção por Capacitação Profissional
- `PROG_MER` - Progressão por Mérito Profissional

### Status do Fluxo
1. `RECEBIDO` - Processo recém-criado
2. `EM_ANALISE` - Em análise pela comissão
3. `PENDENTE_DOCS` - Aguardando documentos
4. `COMPLETO` - Documentação completa
5. `DEFERIDO` - Aprovado
6. `INDEFERIDO` - Reprovado
7. `CANCELADO` - Cancelado pelo requerente

### Documentos Obrigatórios

**PROM_CAP**:
- RG e CPF
- Certificado do Curso
- Declaração da Chefia
- Histórico de Capacitação

**PROG_MER**:
- RG e CPF
- Avaliação de Desempenho
- Declaração da Chefia

### Prazos Legais

| Prazo | Tipo | Dias | Tipo Dia |
|-------|------|------|----------|
| Instrução Inicial | Ambos | 30 | Úteis |
| Análise Capacitação | PROM_CAP | 30 | Úteis |
| Análise Mérito | PROG_MER | 45 | Úteis |
| Complementação Documental | Ambos | 15 | Corridos |

---

## 🛠️ Tecnologias

| Categoria | Tecnologia | Versão |
|-----------|-----------|---------|
| **Backend** | Python | 3.11 |
| | FastAPI | 0.109.0 |
| | SQLAlchemy | 2.0.23 |
| | Uvicorn | 0.27.0 |
| **Frontend** | HTML5 | - |
| | CSS3 | - |
| | JavaScript | ES6+ |
| **Database** | SQLite | 3.x |
| **Importação** | pandas | 2.3.3 |
| | openpyxl | 3.1.5 |

---

## 🧪 Testes

### Testar API Manualmente

```bash
# Ativar ambiente
conda activate pgr-env

# Executar suite de testes
python test_system.py
```

### Testar Endpoints Individualmente

Acesse: http://localhost:8000/docs

Swagger interativo permite testar cada endpoint visualmente.

---

## 📝 Casos de Uso

### 1. Cliente Acompanha Seu Processo

1. Cliente acessa: `https://seu-app.up.railway.app/pgr/`
2. Busca por nome ou matrícula
3. Vê status atualizado, documentos pendentes e prazos

### 2. Servidor Registra Novo Processo

1. Acessa API Docs: `https://seu-app.up.railway.app/docs`
2. Usa endpoint POST `/processes`
3. Sistema cria automaticamente:
   - Checklist de documentos
   - Prazos calculados
   - Status inicial

### 3. Importar Base Histórica

```bash
# Cliente envia planilha_antiga.xlsx
python import_excel.py planilha_antiga.xlsx --test  # Validar
python import_excel.py planilha_antiga.xlsx         # Importar
```

### 4. Monitorar Prazos Vencidos

```bash
# Listar processos com prazos atrasados
curl http://localhost:8000/deadlines/overdue
```

---

## 🔒 Segurança

**Implementado**:
- ✅ CORS configurado
- ✅ Validação de dados (Pydantic)
- ✅ SQL injection protegido (SQLAlchemy)
- ✅ HTTPS no Railway

**Próximos Passos** (produção):
- 🔲 Autenticação JWT
- 🔲 Rate limiting
- 🔲 Logs de auditoria
- 🔲 Backup automático

---

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'fastapi'"
```bash
conda activate pgr-env
pip install -r requirements.txt
```

### Erro: "Database locked"
```bash
# Fechar todas as conexões
pkill -f "uvicorn"
rm -f PGR.db
python seed_sqlalchemy.py
```

### Frontend não carrega
- Verifique se a API está rodando: `curl http://localhost:8000/health`
- Teste no Swagger: `http://localhost:8000/docs`

### Importador falha
```bash
# Validar Excel primeiro
python import_excel.py arquivo.xlsx --test
```

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/pgr-sistema/issues)
- **Docs FastAPI**: https://fastapi.tiangolo.com
- **Docs SQLAlchemy**: https://docs.sqlalchemy.org

---

## 🗺️ Roadmap

### Versão 2.0 (Próxima)
- [ ] Autenticação de usuários (login)
- [ ] Perfis de acesso (admin, servidor, cliente)
- [ ] Upload de documentos (PDF)
- [ ] Notificações por email
- [ ] Relatórios em PDF
- [ ] Histórico de alterações (audit log)
- [ ] Assinatura digital

### Versão 3.0 (Futuro)
- [ ] Integração com sistemas RH
- [ ] App mobile (Flutter)
- [ ] Dashboard de analytics
- [ ] Exportação para sistemas legados
- [ ] API GraphQL

---

## 📜 Licença

Este projeto é de uso interno. Todos os direitos reservados.

---

## 👥 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## ✅ Status do Projeto

- ✅ **Backend**: Completo e testado
- ✅ **Frontend**: Responsivo e funcional
- ✅ **Importador**: Detecta colunas automaticamente
- ✅ **Deploy**: Pronto para Railway.app
- ✅ **Documentação**: Completa

**🎯 Sistema pronto para produção!**

---

**Desenvolvido com ❤️ para modernizar processos administrativos**
