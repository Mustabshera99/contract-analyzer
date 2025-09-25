@echo off
echo ===================================
echo Contract Analyzer - Starting Services
echo ===================================
echo.

echo Starting Backend API on port 8002...
start "Backend API" cmd /k "cd /d "%~dp0" && C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe run_backend.py"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend UI on port 8501...
start "Frontend UI" cmd /k "cd /d "%~dp0" && C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe start_frontend.py"

echo.
echo ===================================
echo Services Starting...
echo ===================================
echo Backend API: http://127.0.0.1:8002
echo Frontend UI: http://localhost:8501
echo API Docs: http://127.0.0.1:8002/docs
echo ===================================
echo.
echo Press any key to exit (this will not stop the services)
pause >nul