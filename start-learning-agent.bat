@echo off
echo Iniciando Learning Agent Web...
cd /d "c:\Users\labin\OneDrive\Documentos\Living_lab\learning_agent_web"
timeout /t 30 /nobreak >nul
docker-compose up -d
echo Learning Agent Web iniciado en http://localhost:8000
timeout /t 5 /nobreak >nul
start http://localhost:8000
