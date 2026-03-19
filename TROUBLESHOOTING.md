# 🔧 Guia de Troubleshooting - Sistema PGR

## Problema: Sistema não está carregando

### 1. Verificar se o servidor está rodando

```bash
# Verificar processos
ps aux | grep "start_app\|uvicorn.*8001" | grep -v grep

# Verificar porta
lsof -i :8001

# Testar servidor
python3 -c "import requests; print(requests.get('http://localhost:8001/').status_code)"
```

**Se não estiver rodando:**
```bash
cd /home/gab/Documentos/PGR
conda activate pgr-env
python3 start_app.py
```

### 2. Verificar frontend buildado

```bash
# Verificar se frontend-dist existe
ls -la frontend-dist/index.html

# Se não existir, buildar:
cd frontend-react
npm install
npm run build
cd ..
```

### 3. Limpar cache do navegador

- **Chrome/Edge**: `Ctrl + Shift + R` ou `Ctrl + F5`
- **Firefox**: `Ctrl + Shift + R` ou `Ctrl + F5`
- Ou abra DevTools (F12) → Network → marque "Disable cache"

### 4. Verificar erros no console do navegador

1. Abra o navegador em `http://localhost:8001`
2. Pressione `F12` para abrir DevTools
3. Vá para a aba **Console**
4. Procure por erros em vermelho
5. Vá para a aba **Network**
6. Recarregue a página (F5)
7. Verifique se os arquivos estão sendo carregados (status 200)

### 5. Verificar se está acessando a URL correta

- ✅ Correto: `http://localhost:8001/`
- ✅ Correto: `http://localhost:8001/login`
- ✅ Correto: `http://localhost:8001/dashboard` (após login)
- ❌ Errado: `http://localhost:8001/api/` (isso é API, não frontend)

### 6. Verificar autenticação

Se a página carrega mas você não consegue fazer login:

```bash
# Verificar se usuário admin existe
conda run -n pgr-env python3 -c "
from backend.database import get_db
from backend.models_sqlalchemy import User
db = next(get_db())
user = db.query(User).filter(User.username == 'admin').first()
print('Admin existe:', user is not None)
if user:
    print('Username:', user.username)
    print('Ativo:', user.is_active)
"
```

**Credenciais padrão:**
- Username: `admin`
- Password: `admin` (ou a senha que você configurou)

### 7. Verificar logs do servidor

O servidor mostra logs no terminal onde foi iniciado. Procure por:
- Erros em vermelho
- Tracebacks
- Mensagens de "ERROR" ou "Exception"

### 8. Reiniciar tudo

```bash
# Parar servidor
pkill -f "python3 start_app.py"

# Aguardar 2 segundos
sleep 2

# Iniciar novamente
cd /home/gab/Documentos/PGR
conda run -n pgr-env python3 start_app.py
```

### 9. Verificar dependências

```bash
conda activate pgr-env
pip install -r requirements.txt
```

### 10. Problemas comuns

#### Página em branco
- Limpe o cache do navegador
- Verifique o console do navegador (F12)
- Verifique se `frontend-dist/index.html` existe

#### Erro 404 em assets
- Rebuilde o frontend: `cd frontend-react && npm run build`
- Verifique se `frontend-dist/assets/` existe

#### Erro de CORS
- O servidor já está configurado para permitir CORS
- Se persistir, verifique se está acessando `localhost` e não `127.0.0.1`

#### Erro de autenticação
- Verifique se está fazendo login corretamente
- Verifique se o token está sendo salvo no localStorage (DevTools → Application → Local Storage)

## Ainda não funciona?

1. Abra o DevTools (F12)
2. Vá para Console
3. Copie TODOS os erros
4. Vá para Network
5. Recarregue a página
6. Veja quais requisições falharam (status vermelho)
7. Compartilhe essas informações
