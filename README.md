# PGR - Sistema de Controle de Processos Administrativos

Sistema completo para gerenciamento de processos administrativos com foco em:
- **Promoção por Capacitação Profissional**
- **Progressão por Mérito Profissional**

## Funcionalidades

✅ Cadastro de processos  
✅ Checklist de documentos obrigatórios  
✅ Controle automático de prazos legais  
✅ Status padronizados  
✅ Campo de parecer e data de efeito financeiro  
✅ API REST completa  
✅ Notificação de prazos vencidos  

## Estrutura do Projeto

```
PGR/
├── schema.sql                  # Schema do banco de dados
├── seed.sql                    # Dados iniciais
├── processes_initial.csv       # CSV inicial de processos
├── models.py                   # Modelos de dados (Python dataclasses)
├── db_utils.py                 # Utilitários de banco de dados
├── create_db.py               # Script de criação do banco
├── api.py                      # API REST (FastAPI)
├── attach_document.py          # CLI para anexar documentos
├── notify_deadlines.py         # CLI para notificar prazos vencidos
├── requirements.txt            # Dependências Python
├── environment.yml             # Ambiente Conda
├── tests/
│   └── test_api.py            # Testes automatizados
└── README.md                   # Este arquivo
```

## Instalação

### Opção 1: Conda (recomendado)

```bash
cd /home/gab/Documentos/PGR
conda env create -f environment.yml
conda activate pgr-env
```

### Opção 2: pip + venv

```bash
cd /home/gab/Documentos/PGR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### 1. Criar banco de dados

```bash
python3 create_db.py
```

Isso irá:
- Criar `PGR.db` (SQLite)
- Aplicar schema e seeds
- Importar processos do CSV
- Gerar checklists e prazos automaticamente

### 2. Executar API

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Acesse:
- Documentação interativa: http://localhost:8000/docs
- API: http://localhost:8000

### 3. Testes

```bash
pytest -v
```

### 4. Scripts CLI

**Anexar documento:**
```bash
python3 attach_document.py PGR-2025-0001 CERT_CURSO 2025-12-15
```

**Verificar prazos vencidos:**
```bash
python3 notify_deadlines.py
python3 notify_deadlines.py --mark  # Marca como notificado
```

## Endpoints da API

### Consultas

- `GET /process-types` - Lista tipos de processo
- `GET /statuses` - Lista status possíveis
- `GET /processes` - Lista processos (com filtros)
- `GET /processes/{protocol}` - Detalhes de um processo
- `GET /deadlines/overdue` - Prazos vencidos
- `GET /deadlines/upcoming?days=7` - Prazos próximos

### Operações

- `POST /processes` - Criar processo
- `PATCH /processes/{protocol}` - Atualizar processo
- `POST /processes/{protocol}/documents/{code}/provide` - Marcar documento fornecido

## Modelo de Dados

### Tabelas principais:

- **process_types**: Tipos de processo (PROM_CAP, PROG_MER)
- **statuses**: Status padronizados
- **processes**: Processos cadastrados
- **documents**: Catálogo de documentos
- **required_documents**: Documentos obrigatórios por tipo
- **process_documents**: Checklist por processo
- **legal_deadlines**: Prazos legais padrão
- **process_deadlines**: Prazos específicos de cada processo

## CSV Inicial

O arquivo `processes_initial.csv` contém exemplos de processos que são importados automaticamente. Você pode editar este arquivo antes de executar `create_db.py`.

Campos:
- `protocol_number`: Número do protocolo (único)
- `type_code`: PROM_CAP ou PROG_MER
- `applicant_name`: Nome do requerente
- `applicant_registration`: Matrícula (opcional)
- `created_date`: Data de criação (YYYY-MM-DD)
- `status_code`: Status inicial
- `parecer`: Parecer técnico (opcional)
- `financial_effective_date`: Data de efeito financeiro (opcional)
- `closed_date`: Data de fechamento (opcional)
- `notes`: Observações (opcional)

## Próximos Passos

Para expandir o sistema, você pode:

1. **Frontend**: Criar interface web (React/Vue)
2. **Notificações por e-mail**: Integrar SMTP
3. **Relatórios**: Gerar relatórios em PDF
4. **Autenticação**: Adicionar login e permissões
5. **Histórico**: Log de alterações
6. **Anexos**: Upload de documentos escaneados

## Licença

Projeto interno - uso institucional.
