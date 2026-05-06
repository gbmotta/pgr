"""
URL pública do webhook para notificações push do Google Drive.
Configure WEBHOOK_BASE_URL no .env (HTTPS, sem barra no final).
"""
import os
from typing import Any, Dict, Optional, Tuple


def build_google_drive_webhook_url() -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Monta a URL completa do endpoint de webhook.

    Returns:
        (url, None) se válida para uso com a API do Google.
        (None, detail_dict) se inválida — use como HTTPException(..., detail=detail_dict).
    """
    base = (os.getenv("WEBHOOK_BASE_URL") or "http://localhost:8001").rstrip("/")
    webhook_url = f"{base}/api/webhooks/google-drive"
    wb_lower = base.lower()

    if "localhost" in wb_lower or "127.0.0.1" in wb_lower or wb_lower.startswith("http://0.0.0.0"):
        return None, {
            "error": "Webhook inacessível (localhost)",
            "message": (
                "Monitoramento automático exige uma URL pública que o Google consiga chamar. "
                "WEBHOOK_BASE_URL está apontando para esta máquina (localhost).\n\n"
                "Configure no .env (raiz do projeto) WEBHOOK_BASE_URL com HTTPS público apontando para este backend "
                "(ex.: ngrok http 8001 → use o https://... sem barra no final). "
                "Exemplo: WEBHOOK_BASE_URL=https://xxxx.ngrok-free.app\n\n"
                "Script auxiliar: ./scripts/pgr.sh tunnel 8001"
            ),
        }

    if webhook_url.startswith("http://"):
        return None, {
            "error": "Webhook precisa usar HTTPS",
            "message": (
                "A URL de notificação do Google Drive deve ser HTTPS. "
                "Ajuste WEBHOOK_BASE_URL para https://... (sem http://) e reinicie o backend."
            ),
        }

    return webhook_url, None
