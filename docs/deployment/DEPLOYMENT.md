# Contract Risk Analyzer Deployment Guide

## Overview

This guide covers deploying the Contract Risk Analyzer application in various environments, from local development to production.

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended (16GB+ for production)
- **Storage**: 50GB+ available space
- **Network**: Internet connection for API calls

### Software Requirements

- **Docker**: 20.10+ with Docker Compose 2.0+
- **Python**: 3.9+ (for local development)
- **Poetry**: 1.4+ (for dependency management)
- **Git**: 2.30+ (for version control)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/contract-analyzer.git
cd contract-analyzer
```

### 2. Choose Deployment Option

**Option A: Zero-Cost Demo (2 minutes)**

```bash
# Enable only local services (no credentials needed)
echo "LOCAL_STORAGE_ENABLED=true" >> .env
echo "LOCAL_PDF_SIGNING_ENABLED=true" >> .env
echo "OPENAI_API_KEY=your_openai_key_here" >> .env
```

**Option B: Full Free Setup (15 minutes)**

```bash
# Run setup script with free alternatives
chmod +x scripts/setup.sh
./scripts/setup.sh --free-alternatives
```

**Option C: Traditional Setup (with paid services)**

```bash
# Run standard setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Start Application

```bash
# Quick start with free alternatives
make quick-start-free

# Or traditional start
make quick-start
```

The application will be available at:

- **Frontend**: http://localhost:8501
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Free Alternatives Deployment

### Zero-Cost Demo Deployment

Perfect for demonstrations and quick testing with no external dependencies:

```bash
# 1. Clone and setup
git clone https://github.com/your-org/contract-analyzer.git
cd contract-analyzer

# 2. Configure for zero-cost demo
cat > .env << EOF
# Core API (required)
OPENAI_API_KEY=your_openai_key_here

# Free alternatives (no credentials needed)
LOCAL_STORAGE_ENABLED=true
LOCAL_PDF_SIGNING_ENABLED=true

# Disable paid services
MICROSOFT_365_ENABLED=false
DOCUSIGN_ENABLED=false
SLACK_ENABLED=false
ANTHROPIC_ENABLED=false
EOF

# 3. Start application
docker-compose up -d

# 4. Verify deployment
curl http://localhost:8000/api/v1/health
```

**What you get:**

- ✅ Contract analysis with OpenAI
- ✅ Local file storage
- ✅ PDF signature generation
- ✅ Complete contract workflow
- 💰 **Cost**: $0 (except OpenAI API usage)

### Full Free Alternatives Deployment

Complete setup with all free services:

```bash
# 1. Setup environment
cat > .env << EOF
# Core API
OPENAI_API_KEY=your_openai_key_here

# Free alternatives
LOCAL_STORAGE_ENABLED=true
LOCAL_PDF_SIGNING_ENABLED=true
DOCUSIGN_SANDBOX_ENABLED=true
OLLAMA_ENABLED=true
GOOGLE_DRIVE_ENABLED=true
HUGGINGFACE_ENABLED=true

# DocuSign Sandbox credentials (free)
DOCUSIGN_SANDBOX_CLIENT_ID=your_sandbox_client_id
DOCUSIGN_SANDBOX_CLIENT_SECRET=your_sandbox_client_secret

# Google Drive credentials (15GB free)
GOOGLE_DRIVE_CLIENT_ID=your_google_client_id
GOOGLE_DRIVE_CLIENT_SECRET=your_google_client_secret
GOOGLE_DRIVE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Hugging Face API key (free tier)
HUGGINGFACE_API_KEY=your_hf_token

# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
EOF

# 2. Install Ollama (if not already installed)
# Visit https://ollama.ai/ and install for your OS
ollama serve
ollama pull llama2

# 3. Start application
docker-compose up -d

# 4. Verify all services
curl http://localhost:8000/api/v1/integrations/status
```

**What you get:**

- ✅ All features from zero-cost demo
- ✅ Electronic signature workflows (DocuSign Sandbox)
- ✅ Local AI analysis (Ollama)
- ✅ Cloud storage (Google Drive)
- ✅ Additional AI models (Hugging Face)
- 💰 **Cost**: $0 (except OpenAI API usage)

### Production Deployment with Free Alternatives

For production environments using free alternatives:

```bash
# 1. Create production environment file
cp config/env.template .env.production

# 2. Configure production settings
cat >> .env.production << EOF
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Free alternatives
LOCAL_STORAGE_ENABLED=true
LOCAL_PDF_SIGNING_ENABLED=true
DOCUSIGN_SANDBOX_ENABLED=true
OLLAMA_ENABLED=true
GOOGLE_DRIVE_ENABLED=true

# Security
SECRET_KEY=your_production_secret_key
JWT_SECRET_KEY=your_jwt_secret_key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/contract_analyzer

# Storage paths
LOCAL_STORAGE_PATH=/app/storage/documents
LOCAL_STORAGE_MAX_SIZE_MB=1000
EOF

# 3. Deploy with Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Setup monitoring (optional)
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Docker Compose Configurations

#### Free Alternatives Docker Compose

```yaml
# docker-compose.free.yml
version: "3.8"
services:
  app:
    build: .
    environment:
      - LOCAL_STORAGE_ENABLED=true
      - LOCAL_PDF_SIGNING_ENABLED=true
      - DOCUSIGN_SANDBOX_ENABLED=true
      - OLLAMA_ENABLED=true
    volumes:
      - ./storage:/app/storage
    ports:
      - "8000:8000"
      - "8501:8501"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0

volumes:
  ollama_data:
```

#### Hybrid Docker Compose

```yaml
# docker-compose.hybrid.yml
version: "3.8"
services:
  app:
    build: .
    environment:
      # Free alternatives
      - LOCAL_STORAGE_ENABLED=true
      - DOCUSIGN_SANDBOX_ENABLED=true
      - OLLAMA_ENABLED=true
      # Paid services (optional)
      - MICROSOFT_365_ENABLED=false
      - DOCUSIGN_ENABLED=false
    volumes:
      - ./storage:/app/storage
    ports:
      - "8000:8000"
      - "8501:8501"
```

### Deployment Verification

After deployment, verify all services are working:

```bash
# Check application health
curl http://localhost:8000/api/v1/health

# Check free alternatives status
curl http://localhost:8000/api/v1/integrations/status

# Test local storage
curl http://localhost:8000/api/v1/integrations/local_storage/stats

# Test DocuSign Sandbox
curl http://localhost:8000/api/v1/integrations/docusign_sandbox/account

# Test Ollama
curl http://localhost:8000/api/v1/integrations/ollama/models

# Test contract analysis
curl -X POST "http://localhost:8000/api/v1/contracts/analyze" \
  -F "file=@sample_contract.pdf" \
  -F "analysis_type=comprehensive"
```

### Cost Comparison by Deployment Type

| Deployment Type    | Setup Time | Monthly Cost | Features            | Best For               |
| ------------------ | ---------- | ------------ | ------------------- | ---------------------- |
| **Zero-Cost Demo** | 2 minutes  | $0           | Local services only | Quick demos            |
| **Full Free**      | 15 minutes | $0           | All free services   | Complete functionality |
| **Hybrid**         | 30 minutes | $5-50        | Mix of free/paid    | Production             |
| **Traditional**    | 45 minutes | $50-200      | All paid services   | Enterprise             |

## Local Development

### Environment Setup

1. **Create Environment File**

   ```bash
   cp config/env.template .env
   # Edit .env with your API keys
   ```

2. **Install Dependencies**

   ```bash
   make install-dev
   ```

3. **Start Services**

   ```bash
   make docker-up
   ```

4. **Create Database Tables**
   ```bash
   make setup-db
   ```

### Development Commands

```bash
# Start all services
make dev start

# Run backend only
make dev backend

# Run frontend only
make dev frontend

# Run tests
make test-all

# Run linting
make lint

# Format code
make format

# View logs
make logs

# Open shell
make shell
```

## Production Deployment

### Docker Deployment

#### 1. Prepare Environment

```bash
# Set production environment
export ENVIRONMENT=production

# Create production .env
cp config/env.template .env.production
# Edit .env.production with production values
```

#### 2. Build and Deploy

```bash
# Build images
make deploy build

# Deploy application
make deploy deploy

# Check status
make deploy status

# View logs
make deploy logs
```

#### 3. Configure Reverse Proxy

**Nginx Configuration** (`/etc/nginx/sites-available/contract-analyzer`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Kubernetes Deployment

#### 1. Create Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: contract-analyzer
```

#### 2. Deploy PostgreSQL

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: contract-analyzer
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:14
          env:
            - name: POSTGRES_DB
              value: contract_analyzer
            - name: POSTGRES_USER
              value: user
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 20Gi
```

#### 3. Deploy Application

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contract-analyzer
  namespace: contract-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contract-analyzer
  template:
    metadata:
      labels:
        app: contract-analyzer
    spec:
      containers:
        - name: backend
          image: contract-analyzer:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secret
                  key: database-url
            - name: REDIS_URL
              value: "redis://redis:6379/0"
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secret
                  key: openai-api-key
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
        - name: frontend
          image: contract-analyzer:latest
          ports:
            - containerPort: 8501
          env:
            - name: BACKEND_URL
              value: "http://localhost:8000"
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "250m"
```

### Cloud Deployment

#### AWS ECS

1. **Create ECS Cluster**

   ```bash
   aws ecs create-cluster --cluster-name contract-analyzer
   ```

2. **Create Task Definition**

   ```json
   {
     "family": "contract-analyzer",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "your-account.dkr.ecr.region.amazonaws.com/contract-analyzer:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "ENVIRONMENT",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "DATABASE_URL",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:contract-analyzer/database-url"
           }
         ]
       }
     ]
   }
   ```

3. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster contract-analyzer \
     --service-name contract-analyzer-service \
     --task-definition contract-analyzer \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

#### Google Cloud Run

1. **Build and Push Image**

   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/contract-analyzer
   ```

2. **Deploy Service**
   ```bash
   gcloud run deploy contract-analyzer \
     --image gcr.io/PROJECT-ID/contract-analyzer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production
   ```

#### Azure Container Instances

1. **Create Resource Group**

   ```bash
   az group create --name contract-analyzer-rg --location eastus
   ```

2. **Deploy Container**
   ```bash
   az container create \
     --resource-group contract-analyzer-rg \
     --name contract-analyzer \
     --image your-registry.azurecr.io/contract-analyzer:latest \
     --dns-name-label contract-analyzer \
     --ports 8000 8501 \
     --environment-variables ENVIRONMENT=production
   ```

## Monitoring Setup

### 1. Start Monitoring Stack

```bash
make monitoring setup
make monitoring start
```

### 2. Access Monitoring Tools

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Jaeger**: http://localhost:16686

### 3. Configure Alerts

Edit `monitoring/alertmanager.yml` to configure alert destinations:

```yaml
global:
  smtp_smarthost: "smtp.gmail.com:587"
  smtp_from: "alerts@yourcompany.com"

route:
  group_by: ["alertname"]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: "email-alerts"

receivers:
  - name: "email-alerts"
    email_configs:
      - to: "admin@yourcompany.com"
        subject: "Contract Analyzer Alert: {{ .GroupLabels.alertname }}"
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

## Security Configuration

### 1. Environment Variables

Set secure environment variables:

```bash
# Generate secure keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Set in .env
echo "SECRET_KEY=$SECRET_KEY" >> .env
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env
```

### 2. Database Security

```bash
# Create database user with limited privileges
CREATE USER contract_analyzer_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE contract_analyzer TO contract_analyzer_user;
GRANT USAGE ON SCHEMA public TO contract_analyzer_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO contract_analyzer_user;
```

### 3. Network Security

```bash
# Configure firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup
make backup-db

# Restore backup
make restore-db BACKUP_FILE=backup_20240120_103000.sql
```

### 2. Application Data Backup

```bash
# Backup application data
tar -czf app_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ logs/

# Restore application data
tar -xzf app_backup_20240120_103000.tar.gz
```

### 3. Automated Backups

Create a cron job for automated backups:

```bash
# Add to crontab
0 2 * * * /path/to/contract-analyzer/scripts/backup.sh
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check service status
make status

# View logs
make logs

# Check resource usage
make stats
```

#### 2. Database Connection Issues

```bash
# Test database connection
make db-shell

# Check database logs
docker-compose logs postgres
```

#### 3. API Not Responding

```bash
# Check API health
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend
```

#### 4. Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Check if backend is accessible
curl http://localhost:8000/api/v1/health
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_contracts_created_at ON contracts(created_at);
CREATE INDEX idx_risks_contract_id ON risks(contract_id);
CREATE INDEX idx_users_username ON users(username);
```

#### 2. Redis Configuration

```yaml
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 3. Application Scaling

```bash
# Scale backend service
make deploy scale backend 3

# Scale frontend service
make deploy scale frontend 2
```

## Maintenance

### 1. Regular Updates

```bash
# Update application
git pull origin main
make deploy update

# Update dependencies
poetry update
```

### 2. Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/contract-analyzer

# Add configuration
/path/to/contract-analyzer/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

### 3. Health Checks

```bash
# Automated health check script
#!/bin/bash
if curl -f http://localhost:8000/health; then
    echo "Application is healthy"
else
    echo "Application is down - restarting"
    make deploy restart
fi
```

## Support

For deployment support:

- **Documentation**: [Deployment Guide](docs/DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@contract-analyzer.com
