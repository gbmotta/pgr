# Como Testar Upload de Planilha XLSX

## 1. Preparar Arquivo de Teste

### Estrutura da Planilha

A planilha deve ter as seguintes colunas (ordem não importa, mas os nomes devem ser exatos ou similares):

**Colunas Obrigatórias (pelo menos uma):**
- `PROCESSO ADM 1DOC` - OU
- `PROCESSO JUDICIAL`

**Colunas Opcionais:**
- `PARTES`
- `DATA RECEBIMENTO (MÊS/ANO)` - Exemplo: "DEZ/2025"
- `TEMA – OBSERVAÇÕES`
- `PRAZO INFO – ESTAG (DIA/MÊS)` - Exemplo: "13/02"
- `PRAZO FINAL (DD/MM)` - Exemplo: "16/02"
- `TIPO DE ATO`
- `DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)` - Exemplo: "15/02/2025"

### Exemplo de Planilha

Crie um arquivo Excel com a seguinte estrutura:

| PROCESSO ADM 1DOC | PROCESSO JUDICIAL | PARTES | DATA RECEBIMENTO (MÊS/ANO) | TEMA – OBSERVAÇÕES | PRAZO FINAL (DD/MM) | TIPO DE ATO |
|-------------------|-------------------|--------|----------------------------|---------------------|---------------------|-------------|
| PGR-2025-001 | | João Silva | DEZ/2025 | Processo de promoção | 20/02 | PARECER |
| | 1234567-89.2025.8.26.0001 | Maria Santos | NOV/2025 | Progressão por mérito | 15/03 | PETIÇÃO |

## 2. Testar via Frontend

### Passo a Passo:

1. **Iniciar o servidor backend:**
   ```bash
   cd /home/gab/Documentos/PGR
   conda activate pgr-env
   python3 start_app.py
   ```

2. **Iniciar o frontend:**
   ```bash
   cd frontend-react
   npm run dev
   ```

3. **Acessar o sistema:**
   - Abra: `http://localhost:5173` (ou porta do Vite)
   - Faça login (admin/admin123)

4. **Ir para página de Upload:**
   - Clique em "Upload" no menu lateral
   - Ou acesse: `http://localhost:5173/upload`

5. **Fazer upload:**
   - Clique em "Upload de Arquivo"
   - Arraste o arquivo XLSX ou clique para selecionar
   - O sistema fará preview e validação automaticamente
   - Revise os erros/avisos se houver
   - Confirme a importação

## 3. Testar via API (cURL)

### Preview (Recomendado primeiro):

```bash
curl -X POST "http://localhost:8001/api/processes/preview-upload" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@/caminho/para/seu/arquivo.xlsx" \
  -F "preview_rows=20"
```

### Upload Direto:

```bash
curl -X POST "http://localhost:8001/processes/upload-excel" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@/caminho/para/seu/arquivo.xlsx"
```

### Obter Token de Autenticação:

```bash
# Login
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use o token retornado no campo "access_token"
```

## 4. Testar com Python

```python
import requests

API_URL = "http://localhost:8001"

# 1. Login
login_response = requests.post(
    f"{API_URL}/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Preview (recomendado)
with open("teste.xlsx", "rb") as f:
    preview_response = requests.post(
        f"{API_URL}/api/processes/preview-upload",
        headers=headers,
        files={"file": f},
        params={"preview_rows": 20}
    )
print("Preview:", preview_response.json())

# 3. Upload
with open("teste.xlsx", "rb") as f:
    upload_response = requests.post(
        f"{API_URL}/processes/upload-excel",
        headers=headers,
        files={"file": f}
    )
print("Upload:", upload_response.json())
```

## 5. Verificar Resultados

### No Dashboard:
- Acesse `http://localhost:5173/dashboard`
- Os processos importados devem aparecer na tabela

### Via API:

```bash
# Listar processos
curl -X GET "http://localhost:8001/processes" \
  -H "Authorization: Bearer SEU_TOKEN"

# Ver histórico de mudanças de um processo
curl -X GET "http://localhost:8001/api/processes/1/history" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## 6. Formato CSV (Alternativa)

O sistema também suporta CSV. Exemplo:

```csv
PROCESSO ADM 1DOC,PROCESSO JUDICIAL,PARTES,DATA RECEBIMENTO (MÊS/ANO),PRAZO FINAL (DD/MM)
PGR-2025-001,,João Silva,DEZ/2025,20/02
,1234567-89.2025.8.26.0001,Maria Santos,NOV/2025,15/03
```

## 7. Troubleshooting

### Erro: "Colunas obrigatórias não encontradas"
- Verifique se os nomes das colunas estão exatos
- O sistema é case-insensitive, mas precisa ser similar
- Exemplo: "Processo ADM 1DOC" funciona, mas "Processo ADM" não

### Erro: "Planilha vazia"
- Verifique se há dados além do cabeçalho
- Remova linhas completamente vazias

### Erro: "É obrigatório informar PROCESSO ADM 1DOC ou PROCESSO JUDICIAL"
- Cada linha deve ter pelo menos um dos identificadores
- Verifique se não há linhas vazias

## 8. Exemplo Completo de Arquivo

Crie um arquivo `teste_processos.xlsx` com:

**Linha 1 (Cabeçalho):**
```
PROCESSO ADM 1DOC | PROCESSO JUDICIAL | PARTES | DATA RECEBIMENTO (MÊS/ANO) | TEMA – OBSERVAÇÕES | PRAZO FINAL (DD/MM) | TIPO DE ATO
```

**Linha 2:**
```
PGR-2025-001 | | João Silva, Maria Santos | DEZ/2025 | Processo de promoção por capacitação profissional | 20/02 | PARECER
```

**Linha 3:**
```
| 1234567-89.2025.8.26.0001 | Maria Santos | NOV/2025 | Progressão por mérito | 15/03 | PETIÇÃO
```
