@echo off
title Contract Analyzer - Full Application
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    CONTRACT ANALYZER                         ║
echo ║                 AI-Powered Contract Analysis                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Starting Contract Analyzer Application...
echo.

cd /d "D:\Agentic AI Projects\AtomCamp Final Project\contract-analyzer\contract-analyzer"

echo [1/2] Starting Backend Server...
start "Contract Analyzer Backend" cmd /k "echo Starting Backend... && C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe simple_backend.py"

echo [2/2] Waiting 5 seconds before starting frontend...
timeout /t 5 /nobreak > nul

echo Starting Frontend Application...
start "Contract Analyzer Frontend" cmd /k "echo Starting Frontend... && C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe -m streamlit run simple_frontend.py --server.port 8501"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                     APPLICATION STARTED                     ║
echo ║                                                              ║
echo ║  Backend:  http://127.0.0.1:8000                           ║
echo ║  Frontend: http://localhost:8501                            ║
echo ║  API Docs: http://127.0.0.1:8000/docs                      ║
echo ║                                                              ║
echo ║  Wait for both services to fully load, then open:           ║
echo ║  → http://localhost:8501                                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Press any key to exit...
pause > nul