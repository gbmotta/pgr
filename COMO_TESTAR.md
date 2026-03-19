# Como Testar Upload de Planilha XLSX

## Método 1: Via Frontend (Recomendado)

### 1. Preparar o arquivo XLSX

Crie um arquivo Excel com estas colunas (ordem não importa):

**Cabeçalhos:**
- `PROCESSO ADM 1DOC` (obrigatório se não tiver PROCESSO JUDICIAL)
- `PROCESSO JUDICIAL` (obrigatório se não tiver PROCESSO ADM 1DOC)
- `PARTES` (opcional)
- `DATA RECEBIMENTO (MÊS/ANO)` (opcional) - Exemplo: "DEZ/2025"
- `TEMA – OBSERVAÇÕES` (opcional)
- `PRAZO INFO – ESTAG (DIA/MÊS)` (opcional) - Exemplo: "13/02"
- `PRAZO FINAL (DD/MM)` (opcional) - Exemplo: "20/02"
- `TIPO DE ATO` (opcional)
- `DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)` (opcional) - Exemplo: "15/02/2025"

**Exemplo de dados:**

| PROCESSO ADM 1DOC | PARTES | DATA RECEBIMENTO (MÊS/ANO) | PRAZO FINAL (DD/MM) |
|-------------------|--------|----------------------------|---------------------|
| PGR-2025-001 | João Silva | DEZ/2025 | 20/02 |
| PGR-2025-002 | Maria Santos | NOV/2025 | 25/03 |

### 2. Iniciar servidores

**Terminal 1 - Backend:**
```bash
cd /home/gab/Documentos/PGR
conda activate pgr-env
python3 start_app.py
```

**Terminal 2 - Frontend:**
```bash
cd /home/gab/Documentos/PGR/frontend-react
npm run dev
```

### 3. Acessar e testar

1. Abra: `http://localhost:5173` (ou porta do Vite)
2. Faça login: `admin` / `admin123`
3. Vá em "Upload" no menu
4. Arraste o arquivo XLSX ou clique para selecionar
5. Clique em "Preview" para ver validação
6. Se tudo OK, clique em "Enviar"

## Método 2: Script Python Automático

```bash
cd /home/gab/Documentos/PGR
conda activate pgr-env
python3 scripts/test_upload.py
```

O script:
- Cria arquivo de exemplo automaticamente
- Testa preview
- Testa upload
- Mostra resultados

## Método 3: Via cURL (API direta)

### 1. Obter token:

```bash
TOKEN=$(python3 -c "
import requests
r = requests.post('http://localhost:8001/api/auth/login', 
  json={'username': 'admin', 'password': 'admin123'})
print(r.json()['access_token'])
")
```

### 2. Preview:

```bash
curl -X POST "http://localhost:8001/api/processes/preview-upload?preview_rows=20" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@teste_processos.xlsx"
```

### 3. Upload:

```bash
curl -X POST "http://localhost:8001/processes/upload-excel" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@teste_processos.xlsx"
```

## Verificar Resultados

### No Dashboard:
- Acesse `http://localhost:5173/dashboard`
- Processos importados aparecem na tabela

### Via API:

```bash
# Listar processos
curl -X GET "http://localhost:8001/processes" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Troubleshooting

### Erro: "Colunas obrigatórias não encontradas"
- Verifique se os nomes das colunas estão corretos
- O sistema é case-insensitive mas precisa ser similar
- Exemplo: "Processo ADM 1DOC" funciona, "Processo ADM" não

### Erro: "Planilha vazia"
- Verifique se há dados além do cabeçalho
- Remova linhas completamente vazias

### Servidor não responde
- Verifique se está rodando: `ps aux | grep uvicorn`
- Verifique porta 8001: `netstat -tuln | grep 8001`
- Reinicie: `python3 start_app.py`

## Exemplo Completo de Planilha

Crie um arquivo `teste.xlsx` com:

**Linha 1 (Cabeçalho):**
```
PROCESSO ADM 1DOC | PROCESSO JUDICIAL | PARTES | DATA RECEBIMENTO (MÊS/ANO) | TEMA – OBSERVAÇÕES | PRAZO FINAL (DD/MM) | TIPO DE ATO
```

**Linha 2:**
```
PGR-2025-001 | | João Silva, Maria Santos | DEZ/2025 | Processo de promoção | 20/02 | PARECER
```

**Linha 3:**
```
| 1234567-89.2025.8.26.0001 | Maria Santos | NOV/2025 | Progressão por mérito | 15/03 | PETIÇÃO
```
