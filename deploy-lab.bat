@echo off
REM Script de despliegue para Windows CMD - Learning Agent Web
REM Uso: deploy-lab.bat

echo 🚀 Desplegando Learning Agent Web en Windows...
echo ===============================================

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker no está instalado
    echo Descárgalo desde: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
    pause
    exit /b 1
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Error: Docker Compose no está disponible
        pause
        exit /b 1
    )
    set DOCKER_COMPOSE_CMD=docker compose
) else (
    set DOCKER_COMPOSE_CMD=docker-compose
)

echo 📋 Verificando requisitos previos...

REM Verificar archivo .env.docker
if not exist ".env.docker" (
    echo ⚠️ Archivo .env.docker no encontrado. Creando uno por defecto...
    (
        echo OPENAI_API_KEY=tu-api-key-aqui
        echo COMPOSE_PROJECT_NAME=learning-agent-lab
        echo LEARNING_AGENT_PORT=8000
        echo DEBUG_MODE=true
        echo REDIS_PORT=6379
    ) > .env.docker
    echo ⚠️ IMPORTANTE: Edita .env.docker con tu API key de OpenAI
    echo Presiona cualquier tecla después de configurar tu API key...
    pause
)

REM Verificar que la API key no sea la por defecto
findstr /C:"tu-api-key-aqui" .env.docker >nul
if not errorlevel 1 (
    echo ❌ Error: Debes configurar tu OPENAI_API_KEY real en .env.docker
    pause
    exit /b 1
)

echo ✅ Requisitos verificados

REM Crear directorios necesarios
echo 📁 Creando directorios de datos...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo ✅ Directorios creados

REM Detener contenedores existentes
echo 🛑 Deteniendo contenedores existentes...
%DOCKER_COMPOSE_CMD% --env-file .env.docker down >nul 2>&1
echo ✅ Contenedores detenidos

REM Construir las imágenes
echo 🔨 Construyendo imágenes Docker...
%DOCKER_COMPOSE_CMD% --env-file .env.docker build
if errorlevel 1 (
    echo ❌ Error: Fallo en la construcción de imágenes
    pause
    exit /b 1
)
echo ✅ Imágenes construidas

REM Iniciar los servicios
echo 🚀 Iniciando servicios...
%DOCKER_COMPOSE_CMD% --env-file .env.docker up -d
if errorlevel 1 (
    echo ❌ Error: Fallo al iniciar servicios
    pause
    exit /b 1
)

REM Esperar a que la aplicación esté lista
echo ⏳ Esperando a que la aplicación esté lista...
timeout /t 10 /nobreak >nul

REM Verificar que la aplicación responde
curl -s http://localhost:8000/api/mcp/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ La aplicación puede tardar un poco más en iniciar
) else (
    echo ✅ Aplicación lista!
)

echo.
echo ===============================================
echo 🎉 ¡Despliegue completado exitosamente!
echo.
echo 📱 Accesos disponibles:
echo    • Aplicación principal: http://localhost:8000
echo    • Documentación API: http://localhost:8000/docs
echo    • Chat con IA: http://localhost:8000/chat
echo    • Dashboard: http://localhost:8000/dashboard
echo    • Herramientas MCP: http://localhost:8000/mcp-tools
echo.
echo 🔧 Comandos útiles:
echo    • Ver logs: %DOCKER_COMPOSE_CMD% --env-file .env.docker logs -f
echo    • Detener: %DOCKER_COMPOSE_CMD% --env-file .env.docker down
echo    • Reiniciar: %DOCKER_COMPOSE_CMD% --env-file .env.docker restart
echo    • Estado: %DOCKER_COMPOSE_CMD% --env-file .env.docker ps
echo.
echo 🌐 Abriendo navegador...
start http://localhost:8000
echo.
echo ===============================================
pause
