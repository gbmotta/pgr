# 🔧 Troubleshooting - Erro de Colunas Obrigatórias

## ❌ Erro: "Colunas obrigatórias não encontradas"

Se você está vendo este erro, significa que o sistema não conseguiu encontrar as colunas obrigatórias na sua planilha.

## ✅ Solução Passo a Passo

### 1. Verifique os Cabeçalhos Exatamente

Os cabeçalhos devem estar **EXATAMENTE** assim (case-insensitive, mas os espaços e caracteres especiais importam):

**Obrigatório (pelo menos um):**
- `PROCESSO ADM 1DOC` 
- `PROCESSO JUDICIAL`

**Opcional:**
- `PARTES`
- `DATA RECEBIMENTO (MÊS/ANO)`
- `TEMA – OBSERVAÇÕES` (note o travessão `–`, não hífen `-`)
- `PRAZO INFO – ESTAG (DIA/MÊS)`
- `PRAZO FINAL (DD/MM)`
- `TIPO DE ATO`
- `DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)`

### 2. Como Criar Corretamente no Google Sheets

**Método 1: Copiar e Colar o CSV**

1. Abra o arquivo `exemplo_planilha_teste.csv` que está em `/docs/`
2. Abra o conteúdo completo
3. Copie TUDO (incluindo a primeira linha com os cabeçalhos)
4. No Google Sheets, clique na célula A1
5. Cole (Ctrl+V ou Cmd+V)
6. O Google Sheets deve detectar automaticamente as colunas

**Método 2: Digitar Manualmente**

Se preferir digitar manualmente, copie EXATAMENTE estes cabeçalhos na linha 1:

```
PROCESSO ADM 1DOC	PROCESSO JUDICIAL	PARTES	DATA RECEBIMENTO (MÊS/ANO)	TEMA – OBSERVAÇÕES	PRAZO INFO – ESTAG (DIA/MÊS)	PRAZO FINAL (DD/MM)	TIPO DE ATO	DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)
```

**IMPORTANTE:**
- Use TAB entre as colunas (não vírgula)
- Ou use vírgula se estiver importando CSV
- Não adicione espaços extras
- Não altere os nomes

### 3. Verificar se os Cabeçalhos Estão Corretos

1. No Google Sheets, verifique a linha 1
2. Certifique-se de que:
   - Não há espaços extras no início ou fim
   - Não há caracteres invisíveis
   - Os nomes estão exatamente como mostrado acima
   - Pelo menos uma das colunas obrigatórias está presente

### 4. Problemas Comuns

**Problema: "Copiei mas não funcionou"**
- ✅ Solução: Use o arquivo CSV diretamente ou copie linha por linha

**Problema: "Os cabeçalhos ficaram em uma única célula"**
- ✅ Solução: Use "Dados" > "Dividir texto em colunas" no Google Sheets
- Ou importe o arquivo CSV usando "Arquivo" > "Importar"

**Problema: "Caracteres especiais não aparecem corretamente"**
- ✅ Solução: Certifique-se de que o encoding está correto (UTF-8)
- Use o travessão `–` (não hífen `-`) em "TEMA – OBSERVAÇÕES"

**Problema: "A planilha está vazia"**
- ✅ Solução: Certifique-se de que há pelo menos uma linha de dados além do cabeçalho

### 5. Template Pronto para Copiar

Copie este bloco COMPLETO e cole no Google Sheets (célula A1):

```
PROCESSO ADM 1DOC	PROCESSO JUDICIAL	PARTES	DATA RECEBIMENTO (MÊS/ANO)	TEMA – OBSERVAÇÕES	PRAZO INFO – ESTAG (DIA/MÊS)	PRAZO FINAL (DD/MM)	TIPO DE ATO	DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)
PGR-2025-001			João Silva; Maria Santos	DEZ/2024	Processo de promoção por capacitação profissional	15/01	20/02/2025	PARECER	18/02/2025
	1234567-89.2025.8.26.0001	Maria Santos; Pedro Costa	NOV/2024	Progressão por mérito	10/02	15/03/2025	PETIÇÃO	12/03/2025
PGR-2025-003			Ana Paula; Carlos Mendes	JAN/2025	Revisão de progressão	20/02	25/03/2025	PARECER	
PGR-2025-004			Roberto Alves	DEZ/2024	Promoção por antiguidade	05/01	10/02/2025	PETIÇÃO	08/02/2025
```

### 6. Verificação Final

Antes de importar, verifique:

- [ ] A linha 1 contém os cabeçalhos
- [ ] Pelo menos uma coluna obrigatória está presente (`PROCESSO ADM 1DOC` OU `PROCESSO JUDICIAL`)
- [ ] Há pelo menos uma linha de dados (linha 2 em diante)
- [ ] Cada linha tem pelo menos um identificador preenchido
- [ ] A planilha foi compartilhada com o Service Account

### 7. Teste Rápido

Se ainda não funcionar, teste com uma planilha mínima:

**Cabeçalho (linha 1):**
```
PROCESSO ADM 1DOC
```

**Dados (linha 2):**
```
PGR-2025-TESTE
```

Isso deve funcionar. Se funcionar, o problema está nos outros cabeçalhos. Se não funcionar, pode haver um problema com o acesso ou formato do arquivo.

## 📞 Ainda com Problemas?

Se após seguir todos os passos ainda houver erro:

1. Verifique se a planilha foi compartilhada corretamente com o Service Account
2. Verifique se o link está correto (deve ser um link do Google Sheets, não do Google Drive)
3. Tente fazer o Preview primeiro para ver se há outros erros
4. Verifique os logs do backend para mais detalhes
