@echo off
echo ================================
echo  Contract Analyzer - Frontend
echo ================================
echo.
echo Starting frontend application...
echo Wait for "You can now view your Streamlit app" message
echo Then open: http://localhost:8501
echo.
cd /d "D:\Agentic AI Projects\AtomCamp Final Project\contract-analyzer\contract-analyzer"
C:/Users/hp/AppData/Local/Programs/Python/Python313/python.exe -m streamlit run simple_frontend.py --server.port 8501
pause