# 📊 Exemplo de Planilha Google Sheets para Teste

## Como usar este exemplo

1. Crie uma nova planilha no Google Sheets
2. Copie e cole o conteúdo abaixo na primeira aba
3. Compartilhe a planilha com o email do Service Account
4. Use o link da planilha no sistema para testar o monitoramento automático

## 📋 Estrutura da Planilha

### Cabeçalho (Linha 1)

Copie exatamente estes cabeçalhos na primeira linha:

```
PROCESSO ADM 1DOC	PROCESSO JUDICIAL	PARTES	DATA RECEBIMENTO (MÊS/ANO)	TEMA – OBSERVAÇÕES	PRAZO INFO – ESTAG (DIA/MÊS)	PRAZO FINAL (DD/MM)	TIPO DE ATO	DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)
```

### Dados de Exemplo (Linhas 2 em diante)

Copie estas linhas de dados:

```
PGR-2025-001			João Silva, Maria Santos	DEZ/2024	Processo de promoção por capacitação profissional	15/01	20/02/2025	PARECER	18/02/2025
	1234567-89.2025.8.26.0001	Maria Santos, Pedro Costa	NOV/2024	Progressão por mérito	10/02	15/03/2025	PETIÇÃO	12/03/2025
PGR-2025-003			Ana Paula, Carlos Mendes	JAN/2025	Revisão de progressão	20/02	25/03/2025	PARECER	
PGR-2025-004			Roberto Alves	DEZ/2024	Promoção por antiguidade	05/01	10/02/2025	PETIÇÃO	08/02/2025
	9876543-21.2025.8.26.0002	Fernanda Lima, José Silva	JAN/2025	Processo administrativo	12/02	18/03/2025	PARECER	15/03/2025
PGR-2025-006			Lucas Oliveira	DEZ/2024	Capacitação profissional	08/01	14/02/2025	PETIÇÃO	12/02/2025
PGR-2025-007			Patricia Souza, Marcos Rocha	JAN/2025	Progressão funcional	25/02	30/03/2025	PARECER	28/03/2025
	1112223-45.2025.8.26.0003	Juliana Costa	FEV/2025	Revisão de processo	15/03	20/04/2025	PETIÇÃO	18/04/2025
PGR-2025-009			Ricardo Santos, Beatriz Almeida	JAN/2025	Promoção por mérito	10/02	15/03/2025	PARECER	13/03/2025
PGR-2025-010			Gabriel Martins	DEZ/2024	Processo de capacitação	03/01	08/02/2025	PETIÇÃO	06/02/2025
```

## 📝 Formato Detalhado (para copiar e colar)

### Versão CSV (mais fácil de copiar)

Copie este bloco completo e cole no Google Sheets:

```csv
PROCESSO ADM 1DOC,PROCESSO JUDICIAL,PARTES,DATA RECEBIMENTO (MÊS/ANO),TEMA – OBSERVAÇÕES,PRAZO INFO – ESTAG (DIA/MÊS),PRAZO FINAL (DD/MM),TIPO DE ATO,DATA DE REALIZAÇÃO DO ATO (DD/MM/YYYY)
PGR-2025-001,,João Silva; Maria Santos,DEZ/2024,Processo de promoção por capacitação profissional,15/01,20/02/2025,PARECER,18/02/2025
,1234567-89.2025.8.26.0001,Maria Santos; Pedro Costa,NOV/2024,Progressão por mérito,10/02,15/03/2025,PETIÇÃO,12/03/2025
PGR-2025-003,,Ana Paula; Carlos Mendes,JAN/2025,Revisão de progressão,20/02,25/03/2025,PARECER,
PGR-2025-004,,Roberto Alves,DEZ/2024,Promoção por antiguidade,05/01,10/02/2025,PETIÇÃO,08/02/2025
,9876543-21.2025.8.26.0002,Fernanda Lima; José Silva,JAN/2025,Processo administrativo,12/02,18/03/2025,PARECER,15/03/2025
PGR-2025-006,,Lucas Oliveira,DEZ/2024,Capacitação profissional,08/01,14/02/2025,PETIÇÃO,12/02/2025
PGR-2025-007,,Patricia Souza; Marcos Rocha,JAN/2025,Progressão funcional,25/02,30/03/2025,PARECER,28/03/2025
,1112223-45.2025.8.26.0003,Juliana Costa,FEV/2025,Revisão de processo,15/03,20/04/2025,PETIÇÃO,18/04/2025
PGR-2025-009,,Ricardo Santos; Beatriz Almeida,JAN/2025,Promoção por mérito,10/02,15/03/2025,PARECER,13/03/2025
PGR-2025-010,,Gabriel Martins,DEZ/2024,Processo de capacitação,03/01,08/02/2025,PETIÇÃO,06/02/2025
```

## ✅ Validações Incluídas

Este exemplo inclui:

- ✅ Processos apenas com PROCESSO ADM 1DOC
- ✅ Processos apenas com PROCESSO JUDICIAL  
- ✅ Processos com ambos os identificadores
- ✅ Diferentes formatos de datas
- ✅ Partes com múltiplas pessoas (separadas por `;` ou `,`)
- ✅ Diferentes tipos de ato (PARECER, PETIÇÃO)
- ✅ Alguns campos opcionais vazios (para testar validação)

## 🧪 Como Testar o Monitoramento Automático

1. **Criar a planilha:**
   - Acesse https://sheets.google.com
   - Crie uma nova planilha
   - Cole o conteúdo acima

2. **Compartilhar com Service Account:**
   - Clique em "Compartilhar" (canto superior direito)
   - Adicione o email: `gmottaz@dashboard-matriarca.iam.gserviceaccount.com`
   - Permissão: "Visualizador"
   - Clique em "Concluído"

3. **Importar no sistema:**
   - Acesse o sistema > Upload > Google Drive
   - Cole o link da planilha
   - Ative "Monitoramento Automático"
   - Clique em "Importar"

4. **Testar sincronização:**
   - Modifique algum dado na planilha do Google Sheets
   - Aguarde alguns segundos
   - Verifique se os dados foram atualizados automaticamente no sistema
   - Veja o histórico em "Planilhas Monitoradas"

## 📌 Observações Importantes

- **Formato de datas:**
  - `PRAZO FINAL (DD/MM)`: Use formato `DD/MM` ou `DD/MM/YYYY` (ex: `20/02` ou `20/02/2025`)
  - `DATA RECEBIMENTO (MÊS/ANO)`: Use formato `MÊS/ANO` (ex: `DEZ/2024`, `JAN/2025`)
  - `DATA DE REALIZAÇÃO DO ATO`: Use formato `DD/MM/YYYY` (ex: `18/02/2025`)

- **Separadores de partes:**
  - Use `;` ou `,` para separar múltiplas partes
  - Exemplo: `João Silva; Maria Santos` ou `João Silva, Maria Santos`

- **Campos obrigatórios:**
  - Cada linha DEVE ter pelo menos um dos seguintes:
    - `PROCESSO ADM 1DOC` OU
    - `PROCESSO JUDICIAL`
  - Se ambos estiverem vazios, a linha será rejeitada

- **Campos opcionais:**
  - Todos os outros campos podem ficar vazios
  - O sistema aceitará a importação mesmo com campos opcionais vazios

## 🔄 Testando Modificações

Após importar, teste fazer modificações na planilha:

1. **Adicionar nova linha:**
   ```
   PGR-2025-011,,Novo Processo Teste,FEV/2025,Teste de sincronização,20/03,25/04/2025,PETIÇÃO,23/04/2025
   ```

2. **Modificar linha existente:**
   - Altere o campo `PARTES` de uma linha existente
   - Altere o `PRAZO FINAL` de uma linha existente

3. **Verificar sincronização:**
   - Acesse "Planilhas Monitoradas"
   - Veja a "Última Sincronização"
   - Verifique se os dados foram atualizados no Dashboard

## 🎯 Resultado Esperado

Após importar esta planilha, você deve ver:

- ✅ 10 processos importados
- ✅ Processos com diferentes tipos (ADM e Judicial)
- ✅ Processos com diferentes prazos (alguns vencidos, alguns futuros)
- ✅ Monitoramento automático ativo
- ✅ Sincronização automática quando você modificar a planilha
