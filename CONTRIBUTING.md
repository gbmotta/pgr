# 🤝 Guia de Contribuição

Obrigado pelo interesse em contribuir com o Sistema PGR! Este documento contém diretrizes para garantir contribuições de qualidade.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Padrões de Código](#padrões-de-código)
- [Commits](#commits)
- [Pull Requests](#pull-requests)
- [Testes](#testes)

---

## 📜 Código de Conduta

- Seja respeitoso e profissional
- Aceite críticas construtivas
- Foque no que é melhor para o projeto
- Mantenha comunicação clara

---

## 🚀 Como Contribuir

### 1. Fork e Clone

```bash
# Fork no GitHub, depois:
git clone https://github.com/SEU-USUARIO/pgr.git
cd pgr
```

### 2. Crie uma Branch

```bash
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
```

Padrões de nome:
- `feature/` - Nova funcionalidade
- `fix/` - Correção de bug
- `docs/` - Documentação
- `refactor/` - Refatoração
- `test/` - Testes

### 3. Configure o Ambiente

```bash
# Criar ambiente
conda env create -f environment.yml
conda activate pgr-env

# Ou com venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Inicializar banco
python -c "from backend.models_sqlalchemy import get_engine, create_tables; create_tables(get_engine())"
python backend/seed_sqlalchemy.py
```

### 4. Faça suas Mudanças

- Siga os padrões de código
- Adicione testes quando aplicável
- Atualize documentação
- Comente código complexo

### 5. Teste

```bash
# Testes automáticos
python scripts/test_system.py

# Testes manuais
uvicorn backend.api_sqlalchemy:app --reload
# Acesse http://localhost:8000/pgr/
```

### 6. Commit e Push

```bash
git add .
git commit -m "tipo: descrição breve"
git push origin feature/nova-funcionalidade
```

### 7. Abra Pull Request

- Descreva o que foi feito
- Mencione issues relacionadas
- Adicione screenshots se aplicável

---

## 💻 Padrões de Código

### Python (PEP 8)

```python
# ✅ Bom
def calcular_prazo(data_inicio: date, dias: int) -> date:
    """
    Calcula data de vencimento do prazo.
    
    Args:
        data_inicio: Data de início do prazo
        dias: Número de dias do prazo
    
    Returns:
        Data de vencimento
    """
    return data_inicio + timedelta(days=dias)

# ❌ Ruim
def calc(d,n):
    return d+timedelta(days=n)
```

**Regras:**
- Nomes descritivos em português
- Docstrings em todas funções
- Type hints quando possível
- 4 espaços de indentação
- Linha máxima: 100 caracteres
- Imports ordenados (stdlib, terceiros, locais)

### JavaScript

```javascript
// ✅ Bom
async function loadProcesses() {
    try {
        const response = await fetch(`${API_URL}/processes`);
        const data = await response.json();
        renderProcesses(data);
    } catch (error) {
        console.error('Erro ao carregar:', error);
        showError(error.message);
    }
}

// ❌ Ruim
function load() {
    fetch(url).then(r=>r.json()).then(d=>render(d))
}
```

**Regras:**
- camelCase para variáveis
- async/await em vez de .then()
- Try-catch para tratamento de erros
- Comentários em português
- 4 espaços de indentação

### SQL/ORM

```python
# ✅ Bom
processes = db.query(Process)\
    .filter(Process.status_code == 'EM_ANALISE')\
    .order_by(Process.created_date.desc())\
    .limit(10)\
    .all()

# ❌ Ruim
p = db.query(Process).filter_by(status_code='EM_ANALISE').all()[:10]
```

---

## 📝 Commits

### Formato

```
tipo: descrição breve (máx 50 caracteres)

Descrição detalhada opcional.
Pode ter múltiplas linhas.

Closes #123
```

### Tipos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta código)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

### Exemplos

```bash
✅ feat: adicionar filtro por data no dashboard
✅ fix: corrigir cálculo de prazos vencidos
✅ docs: atualizar README com novos endpoints
✅ refactor: reorganizar estrutura de pastas
✅ test: adicionar testes para importador Excel
```

---

## 🔍 Pull Requests

### Checklist

Antes de abrir um PR, verifique:

- [ ] Código segue os padrões
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Sem arquivos desnecessários (logs, cache, etc)
- [ ] Commits bem formatados
- [ ] Branch atualizada com main

### Template

```markdown
## Descrição
Breve descrição do que foi feito.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2
3. Resultado esperado

## Screenshots (se aplicável)
[Imagens aqui]

## Issues Relacionadas
Closes #123
```

---

## 🧪 Testes

### Testes Automáticos

```python
# tests/test_api.py
def test_criar_processo():
    response = client.post("/processes", json={
        "protocol_number": "TEST-001",
        "type_code": "PROM_CAP",
        "applicant_name": "Teste",
        "status_code": "RECEBIDO"
    })
    assert response.status_code == 200
```

### Testes Manuais

1. **API**: Teste todos endpoints afetados
2. **Frontend**: Teste em diferentes navegadores
3. **Excel**: Teste upload com arquivos variados
4. **Prazos**: Verifique cálculos de datas
5. **Filtros**: Teste combinações de filtros

---

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 💬 Dúvidas?

- Abra uma [Issue](https://github.com/gbmotta/pgr/issues)
- Entre em contato com o time

---

**Obrigado por contribuir! 🎉**
