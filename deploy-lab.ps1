# Script de despliegue para Windows - Learning Agent Web
# Uso: .\deploy-lab.ps1

Write-Host "🚀 Desplegando Learning Agent Web en Windows..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Función para mostrar errores
function Write-Error-Exit {
    param($Message)
    Write-Host "❌ Error: $Message" -ForegroundColor Red
    exit 1
}

# Función para mostrar éxito
function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

# Función para mostrar advertencias
function Write-Warning-Custom {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Verificar si Docker está instalado
Write-Host "📋 Verificando requisitos previos..." -ForegroundColor Cyan
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error-Exit "Docker no está instalado. Descárgalo desde https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
}

# Verificar si Docker Compose está disponible
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    # Probar con docker compose (nueva sintaxis)
    try {
        docker compose version | Out-Null
        $DockerComposeCmd = "docker compose"
    } catch {
        Write-Error-Exit "Docker Compose no está disponible"
    }
} else {
    $DockerComposeCmd = "docker-compose"
}

# Verificar archivo .env.docker
if (-not (Test-Path ".env.docker")) {
    Write-Warning-Custom "Archivo .env.docker no encontrado. Creando uno por defecto..."
    @"
OPENAI_API_KEY=tu-api-key-aqui
COMPOSE_PROJECT_NAME=learning-agent-lab
LEARNING_AGENT_PORT=8000
DEBUG_MODE=true
REDIS_PORT=6379
"@ | Out-File -FilePath ".env.docker" -Encoding UTF8
    Write-Warning-Custom "⚠️  IMPORTANTE: Edita .env.docker con tu API key de OpenAI antes de continuar"
    $response = Read-Host "¿Has configurado tu OPENAI_API_KEY? (y/N)"
    if ($response -notmatch '^[Yy]$') {
        Write-Error-Exit "Configura tu OPENAI_API_KEY en .env.docker primero"
    }
}

# Verificar que la API key no sea la por defecto
$envContent = Get-Content ".env.docker" -Raw
if ($envContent -match "tu-api-key-aqui") {
    Write-Error-Exit "Debes configurar tu OPENAI_API_KEY real en .env.docker"
}

Write-Success "Requisitos verificados"

# Crear directorios necesarios
Write-Host "📁 Creando directorios de datos..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Success "Directorios creados"

# Detener contenedores existentes si los hay
Write-Host "🛑 Deteniendo contenedores existentes..." -ForegroundColor Cyan
& $DockerComposeCmd --env-file .env.docker down 2>$null
Write-Success "Contenedores detenidos"

# Construir las imágenes
Write-Host "🔨 Construyendo imágenes Docker..." -ForegroundColor Cyan
$buildResult = & $DockerComposeCmd --env-file .env.docker build
if ($LASTEXITCODE -ne 0) {
    Write-Error-Exit "Fallo en la construcción de imágenes"
}
Write-Success "Imágenes construidas"

# Iniciar los servicios
Write-Host "🚀 Iniciando servicios..." -ForegroundColor Cyan
$startResult = & $DockerComposeCmd --env-file .env.docker up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error-Exit "Fallo al iniciar servicios"
}

# Esperar a que la aplicación esté lista
Write-Host "⏳ Esperando a que la aplicación esté lista..." -ForegroundColor Cyan
$maxAttempts = 30
$attempt = 0

do {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/mcp/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "Aplicación lista!"
            break
        }
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Warning-Custom "La aplicación tardó más de lo esperado en iniciar, pero puede estar funcionando"
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "🎉 ¡Despliegue completado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Accesos disponibles:" -ForegroundColor White
Write-Host "   • Aplicación principal: http://localhost:8000" -ForegroundColor White
Write-Host "   • Documentación API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Chat con IA: http://localhost:8000/chat" -ForegroundColor White
Write-Host "   • Dashboard: http://localhost:8000/dashboard" -ForegroundColor White
Write-Host "   • Herramientas MCP: http://localhost:8000/mcp-tools" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Comandos útiles:" -ForegroundColor White
Write-Host "   • Ver logs: $DockerComposeCmd --env-file .env.docker logs -f" -ForegroundColor White
Write-Host "   • Detener: $DockerComposeCmd --env-file .env.docker down" -ForegroundColor White
Write-Host "   • Reiniciar: $DockerComposeCmd --env-file .env.docker restart" -ForegroundColor White
Write-Host "   • Estado: $DockerComposeCmd --env-file .env.docker ps" -ForegroundColor White
Write-Host ""
Write-Host "🏥 Health check:" -ForegroundColor White
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/mcp/health" -ErrorAction Stop
    $healthResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Ejecuta: curl http://localhost:8000/api/mcp/health" -ForegroundColor White
}

Write-Host ""
Write-Host "🌐 Abriendo navegador..." -ForegroundColor Cyan
Start-Process "http://localhost:8000"

Write-Host "===============================================" -ForegroundColor Green
