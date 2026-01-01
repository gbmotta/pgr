# 👤 Guia de Teste - Visão do Cliente

## 🎯 Objetivo
Este guia simula como um cliente/usuario final acessaria e usaria o sistema PGR.

---

## 🌐 Passo 1: Acessar o Sistema

### URL Principal
```
https://web-production-41333.up.railway.app/
```

**Nota:** Se o frontend React ainda não estiver deployado, use:
```
https://web-production-41333.up.railway.app/pgr/
```

---

## 🔐 Passo 2: Fazer Login

### Credenciais Padrão
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **IMPORTANTE:** Em produção, estas credenciais devem ser alteradas!

### Tela de Login
1. Você verá uma tela de login moderna
2. Digite o usuário e senha
3. Clique em **"Entrar"**

---

## 📊 Passo 3: Explorar o Dashboard

Após fazer login, você verá:

### Cards de Resumo
- **Total de Processos** - Número total cadastrado
- **Em Análise** - Processos sendo analisados
- **Docs Pendentes** - Processos aguardando documentos
- **Prazos Vencidos** - Processos com prazos em atraso

### Busca de Processos
- Use a barra de busca para encontrar processos por:
  - Número de protocolo
  - Nome do requerente
  - Matrícula

### Lista de Processos
- Clique em qualquer processo para ver detalhes completos
- Veja status, documentos e prazos

---

## 🔍 Passo 4: Visualizar Detalhes de um Processo

Ao clicar em um processo, você verá:

### Informações Principais
- Número do protocolo
- Nome do requerente
- Tipo de processo (PROM_CAP ou PROG_MER)
- Status atual
- Data de criação
- Matrícula (se houver)

### Checklist de Documentos
- ✅ Documentos entregues (marcados em verde)
- ❌ Documentos pendentes (marcados em vermelho)
- Documentos obrigatórios marcados com *

### Prazos
- Prazo de vencimento
- Status: Cumprido, Pendente ou Vencido
- Dias restantes ou dias vencidos

### Anexos
- Lista de documentos anexados
- Opção de download dos anexos

### Ações Disponíveis
- **Gerar PDF** - Baixa relatório completo em PDF
- **Enviar Documento** - Upload de novos anexos

---

## 📤 Passo 5: Upload de Processos em Lote

### Como fazer upload:
1. Clique em **"Upload"** no menu
2. Prepare uma planilha Excel com:
   - **Coluna Protocolo** (obrigatório)
   - **Coluna Tipo** (PROM_CAP ou PROG_MER)
   - **Coluna Requerente** (nome completo)
   - **Coluna Matrícula** (opcional)
   - **Coluna Data** (opcional)
   - **Coluna Status** (opcional)

3. Arraste e solte o arquivo Excel OU clique para selecionar
4. Clique em **"Enviar"**
5. Aguarde a confirmação de quantos processos foram importados

### Resultado
- Processos serão criados automaticamente
- Checklists de documentos serão gerados
- Prazos legais serão calculados automaticamente

---

## 📄 Passo 6: Gerar Relatório PDF

1. Abra os detalhes de um processo
2. Clique no botão **"Gerar PDF"**
3. O relatório será baixado automaticamente contendo:
   - Dados do processo
   - Checklist de documentos
   - Prazos e status
   - Data de geração

---

## 📋 Passo 7: Visualizar Relatórios e Prazos

### Tela de Relatórios
1. Clique em **"Relatórios"** no menu
2. Veja lista de **Prazos Vencidos**
3. Para cada prazo vencido, você pode:
   - Ver detalhes do processo
   - Gerar relatório PDF
   - Ver quantos dias está vencido

---

## ⚙️ Funcionalidades Avançadas (Se Implementadas)

### Upload de Documento Anexo
1. Abra detalhes de um processo
2. Clique em **"Enviar Documento"**
3. Selecione o arquivo
4. Documento será anexado ao processo

### Atualizar Parecer
- Via API (requer acesso administrativo)
- Endpoint: `PATCH /api/analysis/{request_id}/parecer`

### Aprovar Entregável
- Via API (requer acesso administrativo)
- Endpoint: `POST /api/analysis/deliverable/{id}/approve`

---

## 📱 Responsividade

O sistema é responsivo e funciona em:
- 💻 Desktop
- 📱 Tablet
- 📱 Mobile

Teste redimensionando a janela do navegador.

---

## 🔄 Auto-refresh

O dashboard atualiza automaticamente a cada 30 segundos para mostrar:
- Novos processos
- Mudanças de status
- Atualizações de prazos

---

## ❓ Problemas Comuns

### "Não consigo fazer login"
- Verifique se as credenciais estão corretas
- Verifique se o banco de dados foi inicializado (seed executado)

### "Nenhum processo aparece"
- Execute o seed: `cd backend && python seed_sqlalchemy.py`
- Ou importe processos via Excel

### "Erro ao gerar PDF"
- Verifique se o processo existe
- Verifique logs do servidor

### "Erro ao fazer upload"
- Verifique formato do Excel
- Verifique se as colunas obrigatórias estão presentes

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do Railway
2. Verifique console do navegador (F12)
3. Verifique se a API está respondendo: `/docs`

---

**Última atualização:** 31 de dezembro de 2025

