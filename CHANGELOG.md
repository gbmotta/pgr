# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-12-21

### 🎉 Refatoração Completa

#### Adicionado
- Nova estrutura de pastas organizada:
  - `backend/`: Código Python (API e modelos)
  - `frontend/`: Interface web (HTML/CSS/JS)
  - `scripts/`: Scripts utilitários
  - `docs/`: Documentação consolidada
  - `data/`: Banco de dados SQLite
  - `tests_data/`: Arquivos de teste
  - `archive/`: Código legado
- Documentação completa no `README.md`
- Comentários detalhados em todos os módulos Python
- `backend/__init__.py` com informações do pacote
- CHANGELOG.md para rastreamento de versões

#### Modificado
- Reorganização total da estrutura de arquivos
- Imports atualizados para estrutura modular (`from backend import...`)
- `Procfile` atualizado para `backend.api_sqlalchemy:app`
- Caminho do banco de dados para `data/PGR.db`
- API serve frontend de `frontend/` em vez de `pgr/`
- Melhorias na documentação inline

#### Removido
- Arquivos na raiz (movidos para pastas apropriadas)
- Pasta `pgr/` (renomeada para `frontend/`)
- Código duplicado e não utilizado

---

## [1.5.0] - 2025-12-19

### Adicionado
- Painel de resumo no dashboard com 5 cards informativos:
  - Total de processos
  - Processos em análise
  - Documentos pendentes
  - Prazos vencidos (com alerta vermelho)
  - Prazos próximos (com alerta amarelo)
- Página de upload de Excel (`upload.html`) com:
  - Drag & drop de arquivos
  - Validação client-side
  - Prévia de dados antes de importar
  - Download de template
- Filtros interativos clicando nos cards do resumo
- Upload respeitando coluna "Status" do Excel

### Corrigido
- Cálculo de prazos vencidos e próximos
- Campo `due_date` vs `deadline_date` na API
- Status sempre "RECEBIDO" no upload (agora respeita Excel)
- Comparação de datas com timezone
- Verificação de prazos fechados (`closed=false`)

---

## [1.0.0] - 2025-12-18

### 🚀 Lançamento Inicial

#### Adicionado
- API REST completa com FastAPI
- Modelos SQLAlchemy com 8 tabelas relacionadas
- Dashboard web interativo com:
  - Listagem de processos
  - Busca por protocolo/nome/matrícula
  - Filtros por tipo e status
  - Checklist de documentos
  - Visualização de prazos
  - Auto-refresh (30 segundos)
- Sistema de prazos legais com cálculo automático
- Checklist automático de documentos por tipo de processo
- Importador Excel via linha de comando
- Deploy automatizado no Railway.app
- Testes automatizados de produção
- Documentação básica

#### Tecnologias
- Backend: Python 3.11, FastAPI, SQLAlchemy 2.0
- Frontend: HTML5, CSS3, JavaScript Vanilla
- Banco: SQLite
- Deploy: Railway.app

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Obsoleto` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correções de bugs
- `Segurança` para vulnerabilidades

---

## Links

- [Produção](https://web-production-41333.up.railway.app/pgr/)
- [Repositório](https://github.com/gbmotta/pgr)
- [Documentação](docs/README.md)
