# AWS Bedrock LLM Integration - Setup Anleitung

Diese Anleitung beschreibt, wie AWS Bedrock in das Uni Pilot Backend integriert wird und wie die Authentifizierung über `aws configure` konfiguriert wird.

## Übersicht

Das Backend verwendet AWS Bedrock für LLM-Funktionalitäten:
- **Chat-Service**: Claude 3 Haiku für Konversationen
- **Roadmap-Service**: Claude 3 Sonnet für strukturierte Roadmap-Generierung

Die Authentifizierung erfolgt über die AWS Standard-Credential-Chain, die automatisch folgende Quellen in dieser Reihenfolge prüft:
1. Explizite Credentials in Environment Variables (optional)
2. AWS CLI Credentials (`aws configure`)
3. IAM Role (für EC2/ECS Deployment)

## Schritt 1: AWS Account Setup

### 1.1 AWS Account vorbereiten

1. Stellen Sie sicher, dass Sie Zugriff auf ein AWS Account haben
2. Melden Sie sich in der AWS Console an

### 1.2 Bedrock Model Access aktivieren

1. Navigieren Sie zu **Amazon Bedrock** in der AWS Console
2. Gehen Sie zum Tab **"Model access"** (oder **"Foundation models"**)
3. Klicken Sie auf **"Request model access"** oder **"Enable model"**
4. Aktivieren Sie folgende Modelle:
   - **Anthropic Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`)
   - **Anthropic Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
5. Warten Sie auf die Freischaltung (kann einige Minuten dauern)

### 1.3 IAM Permissions konfigurieren

Erstellen Sie einen IAM User oder Role mit folgenden Permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-*",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-*"
      ]
    }
  ]
}
```

**Wichtig**: Passen Sie die Region (`us-east-1`) an Ihre gewünschte Region an. Verfügbare Regionen:
- `us-east-1` (N. Virginia) - Standard
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)
- Weitere Regionen siehe [AWS Bedrock Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/regions.html)

## Schritt 2: AWS CLI Konfiguration

### 2.1 AWS CLI installieren

Falls noch nicht installiert:

```bash
# macOS
brew install awscli

# Linux
pip install awscli

# Windows
# Download von https://aws.amazon.com/cli/
```

### 2.2 AWS Credentials konfigurieren

Führen Sie `aws configure` aus:

```bash
aws configure
```

Sie werden nach folgenden Informationen gefragt:
- **AWS Access Key ID**: Ihre IAM User Access Key ID
- **AWS Secret Access Key**: Ihr IAM User Secret Access Key
- **Default region name**: z.B. `us-east-1` oder `eu-central-1`
- **Default output format**: `json` (empfohlen)

Die Credentials werden in `~/.aws/credentials` gespeichert.

### 2.3 Konfiguration testen

Testen Sie die Konfiguration:

```bash
# Test mit dem Sample-Script
cd bedrock
python sample.py
```

Erwartete Ausgabe:
```
✅ SUCCESS!
Claude says: Hello from AWS Bedrock!
```

## Schritt 3: Backend Konfiguration

### 3.1 Environment Variables (Optional)

Falls Sie explizite Credentials in Environment Variables setzen möchten (überschreibt `aws configure`):

Erstellen Sie eine `.env` Datei im Projekt-Root:

```env
# AWS Bedrock Configuration
AWS_REGION=us-east-1
# Optional: Nur setzen wenn nicht aws configure verwendet wird
# AWS_ACCESS_KEY_ID=your-access-key-id
# AWS_SECRET_ACCESS_KEY=your-secret-access-key

# LLM Model Configuration
BEDROCK_MODEL_CHAT=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_MODEL_ROADMAP=anthropic.claude-3-sonnet-20240229-v1:0

# LLM Settings
CHAT_TEMPERATURE=0.7
ROADMAP_TEMPERATURE=0.3
MAX_CHAT_HISTORY_MESSAGES=20
```

**Hinweis**: Wenn `AWS_ACCESS_KEY_ID` und `AWS_SECRET_ACCESS_KEY` nicht gesetzt sind, verwendet das Backend automatisch die `aws configure` Credentials.

### 3.2 Region-Konfiguration

Die Region wird in `api/core/config.py` konfiguriert. Standard ist `eu-central-1`, kann aber über Environment Variable `AWS_REGION` überschrieben werden.

**Wichtig**: Die Region muss mit der Region übereinstimmen, in der Sie Bedrock Model Access aktiviert haben.

## Schritt 4: Backend starten und testen

### 4.1 Server starten

```bash
./start_server.sh
# oder
python main.py
```

### 4.2 LLM Service testen

Verwenden Sie die Test-Scripts in `tests/http/` oder die Python-Test-Scripts (siehe unten).

## Schritt 5: Fehlerbehandlung

### Häufige Fehler

1. **"Bedrock client not initialized"**
   - Ursache: AWS Credentials nicht gefunden
   - Lösung: `aws configure` ausführen oder Environment Variables setzen

2. **"AccessDeniedException"**
   - Ursache: IAM Permissions fehlen oder Model Access nicht aktiviert
   - Lösung: IAM Permissions prüfen und Model Access in Bedrock aktivieren

3. **"Model not found"**
   - Ursache: Falsche Model-ID oder Region
   - Lösung: Model-ID und Region in Config prüfen

4. **"Invalid region"**
   - Ursache: Region nicht unterstützt oder falsch geschrieben
   - Lösung: Region auf `us-east-1`, `eu-central-1` oder andere unterstützte Regionen setzen

### Debugging

Aktivieren Sie Logging für detaillierte Fehlermeldungen:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Schritt 6: Deployment

### EC2/ECS Deployment

Für Production-Deployments auf EC2/ECS:

1. Erstellen Sie eine IAM Role mit Bedrock Permissions
2. Weisen Sie die Role der EC2 Instance oder ECS Task zu
3. Entfernen Sie explizite Credentials aus der Config
4. Das Backend verwendet automatisch die IAM Role Credentials

### Lambda Deployment

Für Lambda-Funktionen:

1. Erstellen Sie eine IAM Role mit Bedrock Permissions
2. Weisen Sie die Role der Lambda-Funktion zu
3. Setzen Sie `AWS_REGION` als Environment Variable

## Nächste Schritte

- Testen Sie die Chat-Funktionalität über die API
- Testen Sie die Roadmap-Generierung
- Überwachen Sie AWS CloudWatch für Bedrock API Calls und Kosten

## Referenzen

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [Boto3 Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)

