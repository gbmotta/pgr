#!/usr/bin/env bash
set -euo pipefail

# Bootstrap VPS para PGR (Ubuntu/Debian)
# Uso:
#   bash scripts/bootstrap_vps.sh \
#     --repo https://github.com/SEU_USUARIO/PGR.git \
#     --domain app.seudominio.com \
#     --secret-key "troque-isto" \
#     --webhook-secret "troque-isto"
#
# Opcional:
#   --branch main
#   --app-dir /opt/PGR

REPO_URL=""
APP_DOMAIN=""
SECRET_KEY=""
WEBHOOK_SECRET=""
BRANCH="main"
APP_DIR="/opt/PGR"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_URL="$2"; shift 2 ;;
    --domain)
      APP_DOMAIN="$2"; shift 2 ;;
    --secret-key)
      SECRET_KEY="$2"; shift 2 ;;
    --webhook-secret)
      WEBHOOK_SECRET="$2"; shift 2 ;;
    --branch)
      BRANCH="$2"; shift 2 ;;
    --app-dir)
      APP_DIR="$2"; shift 2 ;;
    -h|--help)
      rg '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *)
      echo "Argumento desconhecido: $1"
      exit 1 ;;
  esac
done

if [[ -z "$REPO_URL" || -z "$APP_DOMAIN" || -z "$SECRET_KEY" || -z "$WEBHOOK_SECRET" ]]; then
  echo "Faltam argumentos obrigatórios."
  echo "Use --help para ver o formato."
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

echo "==> Instalando dependências do sistema"
$SUDO apt update -y
$SUDO apt install -y ca-certificates curl gnupg lsb-release git ufw

echo "==> Instalando Docker Engine + Compose plugin"
if ! command -v docker >/dev/null 2>&1; then
  $SUDO install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  $SUDO chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null
  $SUDO apt update -y
  $SUDO apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

$SUDO systemctl enable docker
$SUDO systemctl start docker

CURRENT_USER="${SUDO_USER:-$USER}"
if id -nG "$CURRENT_USER" | rg -q '\bdocker\b'; then
  echo "==> Usuário já está no grupo docker"
else
  echo "==> Adicionando usuário $CURRENT_USER ao grupo docker"
  $SUDO usermod -aG docker "$CURRENT_USER"
fi

echo "==> Configurando firewall"
$SUDO ufw allow OpenSSH || true
$SUDO ufw allow 80/tcp || true
$SUDO ufw allow 443/tcp || true
$SUDO ufw --force enable || true

echo "==> Clonando/atualizando projeto em $APP_DIR"
$SUDO mkdir -p "$(dirname "$APP_DIR")"
if [[ -d "$APP_DIR/.git" ]]; then
  $SUDO git -C "$APP_DIR" fetch --all
  $SUDO git -C "$APP_DIR" checkout "$BRANCH"
  $SUDO git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
else
  $SUDO git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

echo "==> Gerando arquivo .env de produção"
$SUDO tee "$APP_DIR/.env" >/dev/null <<EOF
APP_DOMAIN=$APP_DOMAIN
WEBHOOK_BASE_URL=https://$APP_DOMAIN
SECRET_KEY=$SECRET_KEY
GOOGLE_WEBHOOK_SECRET=$WEBHOOK_SECRET
EOF

echo "==> Subindo containers"
$SUDO docker compose -f "$APP_DIR/deploy/compose.yml" --env-file "$APP_DIR/.env" up -d --build

echo ""
echo "Bootstrap concluído."
echo "Acesse: https://$APP_DOMAIN"
echo "Logs: sudo docker compose -f $APP_DIR/deploy/compose.yml logs -f"
echo ""
echo "IMPORTANTE:"
echo "- Se o domínio ainda não apontar para este IP, o HTTPS pode demorar/falhar até propagar."
echo "- Se você acabou de entrar no grupo docker, faça logout/login para usar docker sem sudo."
