# Contract Risk Analyzer - Local Development Setup

This guide will help you run the Contract Risk Analyzer application locally without Docker.

## ✅ Prerequisites

- Python 3.11 or higher
- Virtual environment (venv) - already created in this project
- All dependencies are already installed

## 🚀 Quick Start

### Option 1: Run Both Servers Together (Recommended)

```bash
# Activate virtual environment and run both servers
source venv/bin/activate
python run_app.py
```

This will start:

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

### Option 2: Run Servers Separately

**Terminal 1 - Backend:**

```bash
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**

```bash
source venv/bin/activate
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
source venv/bin/activate
python test_contract_analysis.py
```

## 📁 Project Structure

```
contract-analyzer/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── middleware/     # Custom middleware
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── workflows/      # AI workflows
│   └── data/               # ChromaDB data
├── frontend/               # Streamlit frontend
│   ├── components/         # UI components
│   ├── security/           # Security modules
│   └── utils/              # Utilities
├── data/                   # Application data
├── logs/                   # Log files
├── .env                    # Environment configuration
├── run_app.py              # Main startup script
└── test_contract_analysis.py # Test script
```

## ⚙️ Configuration

The application is configured via the `.env` file. Key settings:

- **API Configuration**: Backend runs on port 8000
- **Frontend Configuration**: Frontend runs on port 8501
- **Database**: Uses SQLite and ChromaDB (local files)
- **AI Models**: Configured for OpenAI (requires API key)
- **Security**: Comprehensive security measures enabled

## 🔧 Environment Variables

Key environment variables in `.env`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Frontend Configuration
BACKEND_URL=http://localhost:8000
STREAMLIT_SERVER_PORT=8501

# Database Configuration
SQLITE_ENABLED=true
SQLITE_DATABASE_PATH=./data/contract_analyzer.db
CHROMA_PERSIST_DIRECTORY=./data/chroma

# AI Configuration
OPENAI_API_KEY=sk-test-key-placeholder  # Replace with your actual key
OPENAI_MODEL=gpt-4

# Security Configuration
ENABLE_AUDIT_LOGGING=true
ENABLE_MONITORING=true
```

## 🛠️ Development

### Adding Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements.txt (if needed)
pip freeze > requirements.txt
```

### Running Tests

```bash
# Run all tests
source venv/bin/activate
python -m pytest

# Run specific test file
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=backend
```

### Code Quality

```bash
# Format code
black backend/ frontend/

# Sort imports
isort backend/ frontend/

# Lint code
flake8 backend/ frontend/

# Type checking
mypy backend/ frontend/
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:

   ```bash
   # Kill process using port 8000
   lsof -ti:8000 | xargs kill -9

   # Kill process using port 8501
   lsof -ti:8501 | xargs kill -9
   ```

2. **Import errors**:

   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate

   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **Database errors**:

   ```bash
   # Create data directories
   mkdir -p data/chroma logs
   ```

4. **Permission errors**:
   ```bash
   # Make scripts executable
   chmod +x run_app.py test_contract_analysis.py
   ```

### Logs

Check log files for debugging:

- Application logs: `logs/app.log`
- Audit logs: `logs/audit.log`
- Security logs: `logs/security.log`

## 📊 Monitoring

The application includes comprehensive monitoring:

- **Health Checks**: http://localhost:8000/api/v1/health
- **Detailed Health**: http://localhost:8000/api/v1/health/detailed
- **Monitoring Dashboard**: http://localhost:8000/monitoring/health
- **Prometheus Metrics**: http://localhost:8000/monitoring/metrics/prometheus
- **API Documentation**: http://localhost:8000/docs

## 🔒 Security Features

The application includes enterprise-grade security:

- ✅ File upload validation and malware scanning
- ✅ Input sanitization and injection protection
- ✅ Rate limiting and IP blocking
- ✅ Comprehensive audit logging
- ✅ Secure temporary file management
- ✅ Content Security Policy headers
- ✅ API key management and authentication
- ✅ Memory management and cleanup

## 🎯 Usage

1. **Start the application** using one of the methods above
2. **Open your browser** to http://localhost:8501
3. **Upload a contract** (PDF, DOCX, or TXT)
4. **Analyze the contract** using AI-powered analysis
5. **View results** with risk assessment and recommendations

## 📝 Notes

- The application uses a placeholder OpenAI API key. Replace it with your actual key in `.env`
- All data is stored locally in the `data/` directory
- The application runs in development mode with debug logging enabled
- Security warnings about debug mode are expected in development

## 🆘 Support

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Run the test script: `python test_contract_analysis.py`
3. Verify all dependencies are installed: `pip list`
4. Check the API documentation: http://localhost:8000/docs

---

**🎉 Your Contract Risk Analyzer is now ready to use locally!**
