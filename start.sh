#!/bin/bash

# Contract Risk Analyzer - Local Startup Script
echo "🔒 Contract Risk Analyzer - Starting Local Development"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import fastapi, streamlit, langchain" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not found. Installing..."
    pip install -r requirements.txt
fi

# Run tests
echo "🧪 Running tests..."
python test_contract_analysis.py
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please check the errors above."
    exit 1
fi

# Start the application
echo "🚀 Starting Contract Risk Analyzer..."
echo "📊 Backend API: http://localhost:8000"
echo "🌐 Frontend UI: http://localhost:8501"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

python run_app.py
