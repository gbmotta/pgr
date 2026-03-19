# 📦 Como Instalar Node.js para Buildar o Frontend

## Opção 1: Via apt (Requer sudo)

```bash
sudo apt update
sudo apt install -y nodejs npm
```

Depois verifique:
```bash
node --version
npm --version
```

## Opção 2: Via NVM (Recomendado - Não requer sudo)

```bash
# Instalar NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recarregar o shell
source ~/.bashrc

# Instalar Node.js 18
nvm install 18
nvm use 18

# Verificar
node --version
npm --version
```

## Opção 3: Usar Node.js do sistema (se já estiver instalado)

Verifique se já está instalado:
```bash
which node
which npm
```

## Após Instalar Node.js

Execute para buildar o frontend:

```bash
cd /home/gab/Documentos/PGR/frontend-react
npm install
npm run build
cd ..
rm -rf frontend-dist
cp -r frontend-react/dist frontend-dist
```

## Reiniciar o servidor

Após buildar, reinicie o servidor para ver o novo frontend:

```bash
./run_local.sh
```

