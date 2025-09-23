# API Keys Setup Guide

This guide will help you set up the required API keys for the Contract Risk Analyzer application.

## 🔑 Required API Keys

### 1. OpenAI API Key (✅ Already Configured)

- **Status**: ✅ Already set with your actual key
- **Location**: Already configured in `.env`
- **Usage**: Core AI analysis functionality

### 2. LangSmith API Key (✅ Already Configured)

- **Status**: ✅ Already set with your actual key
- **Location**: Already configured in `.env`
- **Usage**: AI model tracing and monitoring

### 3. Google Drive Integration (❌ Needs Setup)

- **Status**: ❌ Placeholder values need to be replaced
- **Required Keys**:
  - `GOOGLE_DRIVE_CLIENT_ID`
  - `GOOGLE_DRIVE_CLIENT_SECRET`
- **Setup Steps**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a new project or select existing one
  3. Enable Google Drive API
  4. Create OAuth 2.0 credentials
  5. Copy Client ID and Client Secret to `.env` file

### 4. DocuSign Integration (❌ Needs Setup)

- **Status**: ❌ Placeholder values need to be replaced
- **Required Keys**:
  - `DOCUSIGN_SANDBOX_CLIENT_ID`
  - `DOCUSIGN_SANDBOX_CLIENT_SECRET`
- **Setup Steps**:
  1. Go to [DocuSign Developer Center](https://developers.docusign.com/)
  2. Create a new application
  3. Get Client ID and Client Secret
  4. Copy to `.env` file

### 5. Slack Integration (❌ Needs Setup)

- **Status**: ❌ Placeholder values need to be replaced
- **Required Keys**:
  - `SLACK_WEBHOOK_URL`
- **Setup Steps**:
  1. Go to [Slack API](https://api.slack.com/apps)
  2. Create a new app
  3. Enable Incoming Webhooks
  4. Create webhook URL
  5. Copy to `.env` file

### 6. Security Keys (❌ Needs Setup)

- **Status**: ❌ Placeholder values need to be replaced
- **Required Keys**:
  - `API_KEY_SECRET` - For API key validation
  - `JWT_SECRET_KEY` - For JWT token signing
  - `ENCRYPTION_KEY` - For data encryption

## 🛠️ How to Update Keys

### Method 1: Edit .env file directly

```bash
# Open the .env file in your editor
nano .env

# Find the placeholder values and replace them:
GOOGLE_DRIVE_CLIENT_ID=your_actual_google_client_id
GOOGLE_DRIVE_CLIENT_SECRET=your_actual_google_client_secret
DOCUSIGN_SANDBOX_CLIENT_ID=your_actual_docusign_client_id
DOCUSIGN_SANDBOX_CLIENT_SECRET=your_actual_docusign_client_secret
SLACK_WEBHOOK_URL=your_actual_slack_webhook_url
API_KEY_SECRET=your_secure_api_key_secret
JWT_SECRET_KEY=your_secure_jwt_secret
ENCRYPTION_KEY=your_secure_encryption_key
```

### Method 2: Use sed commands

```bash
# Replace Google Drive keys
sed -i '' 's|GOOGLE_DRIVE_CLIENT_ID=your_google_drive_client_id|GOOGLE_DRIVE_CLIENT_ID=YOUR_ACTUAL_ID|g' .env
sed -i '' 's|GOOGLE_DRIVE_CLIENT_SECRET=your_google_drive_client_secret|GOOGLE_DRIVE_CLIENT_SECRET=YOUR_ACTUAL_SECRET|g' .env

# Replace DocuSign keys
sed -i '' 's|DOCUSIGN_SANDBOX_CLIENT_ID=your_docusign_sandbox_client_id|DOCUSIGN_SANDBOX_CLIENT_ID=YOUR_ACTUAL_ID|g' .env
sed -i '' 's|DOCUSIGN_SANDBOX_CLIENT_SECRET=your_docusign_sandbox_client_secret|DOCUSIGN_SANDBOX_CLIENT_SECRET=YOUR_ACTUAL_SECRET|g' .env

# Replace Slack webhook
sed -i '' 's|SLACK_WEBHOOK_URL=your_slack_webhook_url|SLACK_WEBHOOK_URL=YOUR_ACTUAL_WEBHOOK|g' .env
```

## 🔐 Security Key Generation

For the security keys, you can generate secure random keys using:

```bash
# Generate API key secret (32 bytes)
python -c "import secrets; print('API_KEY_SECRET=' + secrets.token_urlsafe(32))"

# Generate JWT secret (32 bytes)
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate encryption key (32 bytes)
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

## ✅ Current Status

- ✅ **OpenAI API**: Working with your actual key
- ✅ **LangSmith API**: Working with your actual key
- ✅ **Core Application**: Fully functional
- ❌ **Google Drive**: Needs actual credentials
- ❌ **DocuSign**: Needs actual credentials
- ❌ **Slack**: Needs actual webhook URL
- ❌ **Security Keys**: Need to be generated

## 🚀 Running the App

The application will work perfectly with just the OpenAI and LangSmith keys. The other integrations are optional and can be added later:

```bash
# Start the application
./start.sh

# Or manually
source venv/bin/activate
python run_app.py
```

## 📝 Notes

- The app is fully functional with just OpenAI and LangSmith keys
- Other integrations are optional features
- You can add the additional keys whenever you're ready
- All placeholder values are clearly marked in the `.env` file
