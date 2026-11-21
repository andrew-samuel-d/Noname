@echo off
title CashFlowScore-ML Server
cd /d "%~dp0"
echo =======================================================
echo  Starting CashFlowScore-ML Server
echo  Opening http://localhost:8000/dashboard in browser...
echo =======================================================
start http://localhost:8000/dashboard
"C:\Users\andre\.local\bin\uv.exe" run uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
pause
