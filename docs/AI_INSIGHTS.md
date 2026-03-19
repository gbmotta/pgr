# Insights Assistidos por IA

Sistema de insights e sugestões assistidos por IA para processos administrativos.

## Características

- **Sugestões de priorização** baseadas em prazos e contexto
- **Resumo de campos longos** (tema/observações, partes)
- **Sinalização de riscos** potenciais
- **Não modifica dados** - apenas fornece sugestões

## Configuração

### Opcional: OpenAI API

Para usar resumos com IA, configure a variável de ambiente:

```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

Sem a chave, o sistema usa processamento simples baseado em regras.

## Endpoints

### `GET /api/processes/{process_id}/insights`

Retorna insights completos para um processo.

**Parâmetros:**
- `include_summary` (default: true) - Incluir resumos
- `include_prioritization` (default: true) - Incluir priorização
- `include_risks` (default: true) - Incluir riscos

**Resposta:**
```json
{
  "process_id": 123,
  "prioritization": {
    "priority_score": 85,
    "priority_level": "high",
    "reasons": ["Prazo próximo: 3 dia(s) restante(s)"],
    "suggestion": "Prioridade HIGH: Prazo próximo: 3 dia(s) restante(s)"
  },
  "summaries": {
    "tema_observacoes": {
      "summary": "Resumo do tema...",
      "is_summarized": true,
      "compression_ratio": 0.45
    }
  },
  "risks": {
    "risk_level": "medium",
    "total_risks": 2,
    "risks": [...]
  }
}
```

### `GET /api/processes/{process_id}/insights/prioritization`

Sugestão de priorização baseada em prazos.

### `GET /api/processes/{process_id}/insights/risks`

Sinalização de riscos potenciais.

### `POST /api/processes/insights/summarize`

Resumir texto longo.

## Garantias

- ✅ **Nunca modifica dados automaticamente**
- ✅ **Apenas sugestões e análises**
- ✅ **Funciona sem IA** (fallback para regras simples)
- ✅ **Rastreável** (timestamp de geração)
