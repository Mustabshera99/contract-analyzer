# Contract Analyzer - Quick Start Guide

## 🚀 How to Run the Application

### Option 1: One-Click Start (Recommended)
**Double-click this file:** `RUN_CONTRACT_ANALYZER.bat`

This will:
- Start the backend server (http://127.0.0.1:8000)
- Start the frontend application (http://localhost:8501)
- Open both in separate windows

### Option 2: Manual Start
1. **Start Backend:** Double-click `start_backend.bat`
2. **Start Frontend:** Double-click `start_frontend.bat`

### Option 3: Command Line
```bash
# Terminal 1 - Backend
python simple_backend.py

# Terminal 2 - Frontend  
streamlit run simple_frontend.py --server.port 8501
```

## 🌐 Access Links

Once both services are running:

- **Main Application**: http://localhost:8501
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 📋 Features Available

### Contract Analysis
- Upload PDF, DOC, DOCX, or TXT files
- Get AI-powered risk assessment
- Receive actionable recommendations
- View confidence scores

### Dashboard
- View contract statistics
- Monitor recent analyses
- Track risk distribution
- Analytics visualizations

## 🔧 Troubleshooting

### If you see "Unable to connect to analysis service":
1. Make sure backend is running (check http://127.0.0.1:8000)
2. Wait 10-15 seconds for services to fully start
3. Refresh the frontend page
4. Check that no firewall is blocking ports 8000 or 8501

### If ports are already in use:
1. Close any existing browser tabs with the app
2. Stop any running Python processes
3. Restart using the batch files

### If you get import errors:
1. Make sure all dependencies are installed
2. Run: `pip install -r requirements.txt`
3. Or install missing packages individually

## 📂 File Structure
```
contract-analyzer/
├── RUN_CONTRACT_ANALYZER.bat     ← Main startup script
├── start_backend.bat             ← Backend only
├── start_frontend.bat            ← Frontend only  
├── simple_backend.py             ← Backend server
├── simple_frontend.py            ← Frontend app
└── requirements.txt              ← Dependencies
```

## 🎯 Quick Test
1. Run `RUN_CONTRACT_ANALYZER.bat`
2. Wait for both services to start
3. Open http://localhost:8501
4. Upload a sample contract file
5. Click "Analyze Contract"
6. View the results!

---
**Need Help?** Check the terminal windows for error messages or contact support.