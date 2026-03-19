# Google Sheets Dynamic Integration - Setup Guide

## Overview

The system now supports dynamic Google Sheets integration using Google Drive watch channels and webhooks. When a linked Google Sheet is modified, the system automatically receives notifications and updates internal records.

## Architecture

- **Google Drive API**: Watch channels for file change notifications
- **Google Sheets API**: Fetch updated spreadsheet data
- **Webhook Endpoint**: Receives change notifications from Google
- **Service Account**: Authenticates with Google APIs

## Prerequisites

1. Google Cloud Project with Drive API and Sheets API enabled
2. Service Account with appropriate permissions
3. Service Account JSON credentials file
4. Public webhook URL (for production)

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API** and **Google Sheets API**

### 2. Create Service Account

1. Navigate to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: `pgr-sheets-service`
4. Grant roles:
   - **Service Account User**
5. Click **Create Key** > **JSON**
6. Save the JSON file securely

### 3. Share Google Sheets with Service Account

For each Google Sheet you want to link:

1. Open the Google Sheet
2. Click **Share**
3. Add the Service Account email (from JSON file, field `client_email`)
4. Grant **Viewer** permission
5. Copy the Sheet URL

### 4. Configure Environment Variables

Create `.env` file or set environment variables:

```bash
# Path to Service Account JSON file
GOOGLE_CREDENTIALS_PATH=credentials/service_account.json

# Base URL for webhook endpoint (must be publicly accessible)
WEBHOOK_BASE_URL=https://your-domain.com

# Optional: Secret token for webhook verification
GOOGLE_WEBHOOK_SECRET=your-secret-token-here
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies:
- `google-api-python-client>=2.100.0`
- `google-auth>=2.23.0`
- `google-auth-httplib2>=0.1.1`
- `google-auth-oauthlib>=1.1.0`

### 6. Database Migration

The `LinkedSheet` model is automatically created when the application starts. To manually create:

```python
from backend import models_sqlalchemy as models
engine = models.get_engine()
models.create_tables(engine)
```

## Usage

### Link a Google Sheet

**Endpoint:** `POST /api/sheets/link`

**Request:**
```json
{
  "url": "https://docs.google.com/spreadsheets/d/FILE_ID/edit"
}
```

**Response:**
```json
{
  "status": "linked",
  "file_id": "FILE_ID",
  "channel_id": "channel-uuid",
  "expiration": 1234567890000
}
```

### List Linked Sheets

**Endpoint:** `GET /api/sheets/linked`

**Response:**
```json
[
  {
    "id": 1,
    "file_id": "FILE_ID",
    "url": "https://docs.google.com/spreadsheets/d/FILE_ID/edit",
    "last_sync": "2025-01-13T10:30:00",
    "expiration": "2025-01-20T10:30:00"
  }
]
```

### Unlink a Google Sheet

**Endpoint:** `DELETE /api/sheets/link/{file_id}`

**Response:**
```json
{
  "status": "unlinked",
  "file_id": "FILE_ID"
}
```

## Webhook Endpoint

**Endpoint:** `POST /api/webhooks/google-drive`

This endpoint is called automatically by Google when a linked sheet is modified. It:
1. Verifies the webhook request
2. Identifies the linked sheet by resource_id
3. Fetches updated data from Google Sheets
4. Processes and imports new/updated records
5. Updates last_sync timestamp

## How It Works

1. **Link Creation**: When you link a sheet, the system:
   - Extracts file_id from URL
   - Creates a Drive watch channel
   - Stores channel metadata in database

2. **Change Detection**: When sheet is modified:
   - Google sends webhook to `/api/webhooks/google-drive`
   - System identifies linked sheet
   - Fetches updated data via Sheets API

3. **Data Processing**: 
   - Parses spreadsheet data
   - Imports new processes
   - Updates existing records (if applicable)
   - Updates last_sync timestamp

4. **Channel Renewal**: Watch channels expire after 7 days. Implement a cron job to renew channels before expiration.

## Security

### Webhook Verification

Set `GOOGLE_WEBHOOK_SECRET` environment variable to enable token verification. The webhook handler compares the `X-Goog-Channel-Token` header with the secret.

### Service Account Security

- Store credentials file securely
- Never commit credentials to version control
- Use environment variables for paths
- Rotate credentials periodically

## Troubleshooting

### Webhook Not Receiving Notifications

1. Verify webhook URL is publicly accessible
2. Check firewall/security group rules
3. Verify channel is active in database
4. Check Google Cloud Console for API quotas

### Authentication Errors

1. Verify Service Account JSON file path
2. Check Service Account has required APIs enabled
3. Verify Sheet is shared with Service Account email
4. Check credentials file format is valid JSON

### Import Errors

1. Verify sheet has required columns (Protocolo, Tipo, Requerente)
2. Check data format matches expected schema
3. Review error messages in webhook response
4. Check database connection and permissions

## Channel Renewal

Watch channels expire after 7 days. Implement a background task to renew channels:

```python
from backend import drive_service, models_sqlalchemy as models
from datetime import datetime, timedelta

def renew_expiring_channels():
    engine = models.get_engine()
    db = models.get_session(engine)
    
    expiration_threshold = datetime.utcnow() + timedelta(days=1)
    
    expiring = db.query(models.LinkedSheet).filter(
        models.LinkedSheet.expiration < expiration_threshold,
        models.LinkedSheet.is_active == True
    ).all()
    
    for sheet in expiring:
        # Renew channel logic
        pass
```

## Production Considerations

1. **HTTPS Required**: Webhook URL must use HTTPS
2. **Load Balancer**: Ensure webhook endpoint is behind load balancer
3. **Idempotency**: Webhook handler is idempotent (safe to retry)
4. **Monitoring**: Monitor webhook endpoint for errors
5. **Logging**: Log all webhook events for debugging
6. **Rate Limiting**: Implement rate limiting on webhook endpoint
