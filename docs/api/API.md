# Contract Risk Analyzer API Documentation

## Overview

The Contract Risk Analyzer provides a comprehensive REST API for contract analysis, risk assessment, and document management. The API is built with FastAPI and provides automatic interactive documentation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Health & Status

#### GET /health

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "1.0.0"
}
```

#### GET /api/v1/health

Detailed health check with service status.

**Response:**

```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "chroma": "healthy"
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Contract Analysis

#### POST /api/v1/contracts/analyze

Analyze a contract for risks and provide recommendations.

**Request Body:**

```json
{
  "file_path": "path/to/contract.pdf",
  "analysis_type": "comprehensive",
  "risk_categories": ["financial", "legal", "operational"],
  "confidence_threshold": 0.7
}
```

**Response:**

```json
{
  "analysis_id": "uuid-string",
  "status": "completed",
  "risks": [
    {
      "id": "risk-1",
      "category": "financial",
      "severity": "high",
      "description": "Payment terms are unfavorable",
      "confidence": 0.85,
      "recommendations": [
        "Negotiate better payment terms",
        "Add late payment penalties"
      ]
    }
  ],
  "summary": {
    "total_risks": 5,
    "high_risk_count": 2,
    "medium_risk_count": 2,
    "low_risk_count": 1
  },
  "created_at": "2024-01-20T10:30:00Z"
}
```

#### GET /api/v1/contracts/{analysis_id}

Get analysis results by ID.

**Response:**

```json
{
  "analysis_id": "uuid-string",
  "status": "completed",
  "risks": [...],
  "summary": {...},
  "created_at": "2024-01-20T10:30:00Z"
}
```

#### GET /api/v1/contracts

List all contract analyses with pagination.

**Query Parameters:**

- `page`: Page number (default: 1)
- `size`: Page size (default: 10)
- `status`: Filter by status
- `category`: Filter by risk category

**Response:**

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

### Free Alternatives Integration

#### GET /api/v1/integrations/status

Get status of all available integrations (paid and free).

**Response:**

```json
{
  "integrations": {
    "local_storage": {
      "status": "active",
      "cost": "free",
      "features": ["file_storage", "metadata_tracking"]
    },
    "google_drive": {
      "status": "inactive",
      "cost": "free",
      "features": ["cloud_storage", "collaboration"]
    },
    "docusign_sandbox": {
      "status": "active",
      "cost": "free",
      "features": ["electronic_signatures", "workflow_management"]
    },
    "ollama": {
      "status": "active",
      "cost": "free",
      "features": ["local_ai", "offline_processing"]
    }
  }
}
```

#### Local Storage Service

##### GET /api/v1/integrations/local_storage/documents

List documents in local storage.

**Query Parameters:**

- `folder`: Folder name (default: "contracts")
- `page`: Page number
- `size`: Page size

**Response:**

```json
{
  "documents": [
    {
      "document_id": "contract_001.pdf",
      "title": "Service Agreement",
      "file_type": ".pdf",
      "size": 1024000,
      "created_at": "2024-01-20T10:30:00Z",
      "modified_at": "2024-01-20T10:30:00Z",
      "metadata": {
        "folder": "contracts",
        "tags": ["legal", "service"]
      }
    }
  ],
  "total": 25,
  "page": 1,
  "size": 10
}
```

##### POST /api/v1/integrations/local_storage/upload

Upload a document to local storage.

**Request Body:**

- `file`: File content (multipart/form-data)
- `folder`: Target folder (default: "contracts")
- `metadata`: Optional metadata (JSON)

**Response:**

```json
{
  "document_id": "contract_002.pdf",
  "status": "uploaded",
  "path": "/app/storage/documents/contracts/contract_002.pdf",
  "size": 2048000
}
```

##### GET /api/v1/integrations/local_storage/stats

Get local storage statistics.

**Response:**

```json
{
  "total_size_bytes": 104857600,
  "total_size_mb": 100.0,
  "max_size_mb": 100,
  "file_count": 25,
  "base_path": "/app/storage/documents",
  "enabled": true
}
```

#### DocuSign Sandbox Service

##### GET /api/v1/integrations/docusign_sandbox/account

Get DocuSign Sandbox account information.

**Response:**

```json
{
  "account_id": "sandbox-account-123",
  "account_name": "Demo Account",
  "base_url": "https://demo.docusign.net",
  "status": "active"
}
```

##### POST /api/v1/integrations/docusign_sandbox/envelope

Create a DocuSign envelope for signature.

**Request Body:**

```json
{
  "document_content": "base64-encoded-pdf",
  "document_name": "Contract Agreement",
  "recipients": [
    {
      "email": "signer@example.com",
      "name": "John Doe",
      "role": "signer"
    }
  ],
  "subject": "Please sign this contract",
  "message": "Please review and sign the attached contract."
}
```

**Response:**

```json
{
  "envelope_id": "envelope-123",
  "status": "sent",
  "subject": "Please sign this contract",
  "created_date_time": "2024-01-20T10:30:00Z",
  "documents_uri": "/envelopes/envelope-123/documents",
  "recipients_uri": "/envelopes/envelope-123/recipients"
}
```

#### Local PDF Signing Service

##### POST /api/v1/integrations/local_pdf_signing/template

Create a signature template.

**Request Body:**

```json
{
  "signer_name": "John Doe",
  "signer_email": "john@example.com",
  "contract_title": "Service Agreement"
}
```

**Response:**

```json
{
  "template_id": "template-123",
  "pdf_content": "base64-encoded-pdf",
  "status": "created"
}
```

##### POST /api/v1/integrations/local_pdf_signing/sign

Add signatures to a PDF.

**Request Body:**

```json
{
  "pdf_content": "base64-encoded-pdf",
  "signatures": [
    {
      "signer_name": "John Doe",
      "signer_email": "john@example.com",
      "signature_text": "John Doe",
      "x_position": 100,
      "y_position": 100,
      "page_number": 1
    }
  ]
}
```

**Response:**

```json
{
  "signed_pdf": "base64-encoded-signed-pdf",
  "status": "signed",
  "signature_count": 1
}
```

#### Ollama Service

##### GET /api/v1/integrations/ollama/models

List available Ollama models.

**Response:**

```json
{
  "models": [
    {
      "name": "llama2",
      "size": "3.8GB",
      "modified_at": "2024-01-20T10:30:00Z"
    },
    {
      "name": "mistral",
      "size": "4.1GB",
      "modified_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

##### POST /api/v1/integrations/ollama/chat

Send a chat completion request to Ollama.

**Request Body:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze this contract for risks"
    }
  ],
  "model": "llama2",
  "temperature": 0.1,
  "max_tokens": 1000
}
```

**Response:**

```json
{
  "model": "llama2",
  "message": {
    "role": "assistant",
    "content": "I'll analyze the contract for potential risks..."
  },
  "done": true,
  "total_duration": 1500
}
```

### Analytics

#### GET /api/v1/analytics/risk-trends

Get risk trend analysis over time.

**Query Parameters:**

- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `category`: Risk category filter

**Response:**

```json
{
  "trends": [
    {
      "date": "2024-01-20",
      "total_risks": 15,
      "high_risks": 3,
      "medium_risks": 8,
      "low_risks": 4
    }
  ],
  "summary": {
    "average_risks_per_day": 12.5,
    "trend_direction": "increasing"
  }
}
```

#### GET /api/v1/analytics/contract-comparison

Compare multiple contracts.

**Request Body:**

```json
{
  "contract_ids": ["uuid1", "uuid2", "uuid3"],
  "comparison_type": "risk_analysis"
}
```

**Response:**

```json
{
  "comparison_id": "uuid-string",
  "contracts": [
    {
      "contract_id": "uuid1",
      "risk_score": 7.5,
      "key_risks": [...]
    }
  ],
  "insights": [
    "Contract A has higher financial risks",
    "Contract B has better terms overall"
  ]
}
```

#### GET /api/v1/analytics/compliance

Check compliance against standards.

**Query Parameters:**

- `standard`: Compliance standard (e.g., "SOX", "GDPR")
- `contract_id`: Specific contract ID

**Response:**

```json
{
  "compliance_score": 85.5,
  "violations": [
    {
      "clause": "Data Protection",
      "severity": "medium",
      "description": "Missing data retention policy"
    }
  ],
  "recommendations": ["Add data retention clause", "Include privacy notice"]
}
```

### Security & Authentication

#### POST /api/v1/auth/register

Register a new user.

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response:**

```json
{
  "user_id": "uuid-string",
  "username": "john_doe",
  "email": "john@example.com",
  "status": "active",
  "created_at": "2024-01-20T10:30:00Z"
}
```

#### POST /api/v1/auth/login

Authenticate user and get JWT token.

**Request Body:**

```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**

```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid-string",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### POST /api/v1/auth/mfa/enable

Enable MFA for user.

**Request Body:**

```json
{
  "user_id": "uuid-string"
}
```

**Response:**

```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "secret_key": "JBSWY3DPEHPK3PXP",
  "backup_codes": ["12345678", "87654321"]
}
```

#### POST /api/v1/auth/mfa/verify

Verify MFA token.

**Request Body:**

```json
{
  "user_id": "uuid-string",
  "token": "123456"
}
```

**Response:**

```json
{
  "verified": true,
  "message": "MFA verification successful"
}
```

### Monitoring

#### GET /api/v1/monitoring/metrics

Get application metrics.

**Response:**

```json
{
  "metrics": [
    {
      "name": "http_requests_total",
      "value": 1250,
      "labels": {
        "method": "POST",
        "endpoint": "/api/v1/contracts/analyze"
      }
    }
  ],
  "timestamp": "2024-01-20T10:30:00Z"
}
```

#### GET /api/v1/monitoring/anomalies

Get detected anomalies.

**Query Parameters:**

- `metric_name`: Specific metric name
- `severity`: Anomaly severity level

**Response:**

```json
{
  "anomalies": [
    {
      "metric_name": "response_time",
      "is_anomaly": true,
      "anomaly_score": 0.95,
      "timestamp": "2024-01-20T10:30:00Z",
      "expected_value": 0.5,
      "actual_value": 2.3
    }
  ]
}
```

### Integrations

#### GET /api/v1/integrations/microsoft-365/files

List files from Microsoft 365.

**Query Parameters:**

- `folder_path`: Specific folder path
- `file_type`: File type filter

**Response:**

```json
{
  "files": [
    {
      "id": "file-id",
      "name": "contract.pdf",
      "size": 1024000,
      "modified_at": "2024-01-20T10:30:00Z",
      "download_url": "https://graph.microsoft.com/v1.0/me/drive/items/file-id/content"
    }
  ]
}
```

#### POST /api/v1/integrations/microsoft-365/upload

Upload file to Microsoft 365.

**Request Body:**

```json
{
  "file_path": "path/to/file.pdf",
  "folder_path": "Documents/Contracts",
  "file_name": "new_contract.pdf"
}
```

**Response:**

```json
{
  "file_id": "new-file-id",
  "upload_url": "https://graph.microsoft.com/v1.0/me/drive/items/new-file-id",
  "status": "uploaded"
}
```

#### GET /api/v1/integrations/docusign/envelopes

List DocuSign envelopes.

**Response:**

```json
{
  "envelopes": [
    {
      "envelope_id": "envelope-id",
      "status": "sent",
      "subject": "Contract Agreement",
      "created_at": "2024-01-20T10:30:00Z",
      "recipients": [
        {
          "email": "signer@example.com",
          "status": "signed"
        }
      ]
    }
  ]
}
```

#### POST /api/v1/integrations/docusign/send

Send document for signature.

**Request Body:**

```json
{
  "document_path": "path/to/contract.pdf",
  "recipients": [
    {
      "email": "signer@example.com",
      "name": "John Doe",
      "role": "signer"
    }
  ],
  "subject": "Contract Agreement",
  "message": "Please review and sign the contract"
}
```

**Response:**

```json
{
  "envelope_id": "envelope-id",
  "status": "sent",
  "signing_url": "https://demo.docusign.net/signing/...",
  "created_at": "2024-01-20T10:30:00Z"
}
```

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format.

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-20T10:30:00Z",
  "request_id": "uuid-string"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Per User**: 60 requests per minute
- **Per IP**: 1000 requests per hour
- **Burst**: 10 requests per second

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642680000
```

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (1-based)
- `size`: Number of items per page (max 100)
- `sort`: Sort field and direction (e.g., "created_at:desc")

Pagination metadata is included in the response:

```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events

- `contract.analysis.completed`
- `contract.analysis.failed`
- `user.registered`
- `user.login.failed`
- `system.alert.triggered`

### Webhook Payload

```json
{
  "event": "contract.analysis.completed",
  "data": {
    "analysis_id": "uuid-string",
    "user_id": "uuid-string",
    "status": "completed"
  },
  "timestamp": "2024-01-20T10:30:00Z",
  "signature": "sha256=..."
}
```

## SDKs and Examples

### Python SDK

```python
from contract_analyzer import ContractAnalyzer

client = ContractAnalyzer(api_key="your-api-key")

# Analyze contract
result = client.analyze_contract("path/to/contract.pdf")
print(f"Found {len(result.risks)} risks")

# Get analytics
trends = client.get_risk_trends(start_date="2024-01-01")
```

### JavaScript SDK

```javascript
import { ContractAnalyzer } from "contract-analyzer-js";

const client = new ContractAnalyzer("your-api-key");

// Analyze contract
const result = await client.analyzeContract("path/to/contract.pdf");
console.log(`Found ${result.risks.length} risks`);
```

### cURL Examples

```bash
# Analyze contract
curl -X POST "http://localhost:8000/api/v1/contracts/analyze" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "contract.pdf"}'

# Get risk trends
curl -X GET "http://localhost:8000/api/v1/analytics/risk-trends?start_date=2024-01-01" \
  -H "Authorization: Bearer your-jwt-token"
```

## Interactive Documentation

The API provides interactive documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Support

For API support and questions:

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture including free alternatives
- [User Guide](USER_GUIDE.md) - User instructions for free alternatives setup and usage
- [Deployment Guide](DEPLOYMENT.md) - Deployment options including free alternatives
- [FAQ](FAQ.md) - Frequently asked questions about free alternatives
- [Troubleshooting](TROUBLESHOOTING.md) - Free alternatives troubleshooting guide
- [Main README](../README.md) - Project overview and quick start guide
- **Email**: support@contract-analyzer.com
