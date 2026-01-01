# 🔐 Como Configurar SSH para Git (Sem Pedir Senha)

## ✅ Chave SSH Gerada!

Sua chave SSH foi gerada com sucesso. Agora siga estes passos:

## 📋 Passo a Passo

### 1. Copiar a Chave Pública

A chave pública já foi exibida no terminal. Ela é algo como:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... gbmotta@gmail.com
```

### 2. Adicionar no GitHub

1. Acesse: **https://github.com/settings/keys**
2. Clique em **"New SSH key"**
3. **Title**: Digite um nome (ex: "PC Trabalho" ou "Laptop")
4. **Key**: Cole a chave pública completa (começa com `ssh-ed25519`)
5. Clique em **"Add SSH key"**

### 3. Testar Conexão

```bash
ssh -T git@github.com
```

Você deve ver: `Hi gbmotta! You've successfully authenticated...`

### 4. Configurar Git para Usar SSH

Depois de adicionar a chave no GitHub, execute:

```bash
cd /home/gab/Documentos/PGR
git remote set-url origin git@github.com:gbmotta/pgr.git
```

### 5. Testar Push

```bash
git push
```

Agora não deve pedir senha mais! 🎉

---

## 🔄 Alternativa: Credential Helper (Mais Simples, Menos Seguro)

Se preferir usar HTTPS com senha salva:

```bash
# Salvar credenciais por 1 hora
git config --global credential.helper cache

# OU salvar permanentemente (menos seguro)
git config --global credential.helper store
```

---

## 📝 Comandos Úteis

```bash
# Ver remote atual
git remote -v

# Mudar para SSH
git remote set-url origin git@github.com:gbmotta/pgr.git

# Mudar de volta para HTTPS
git remote set-url origin https://github.com/gbmotta/pgr.git

# Ver chaves SSH
cat ~/.ssh/id_ed25519.pub

# Testar conexão SSH
ssh -T git@github.com
```

---

**Última atualização:** 31 de dezembro de 2025

