# Guía de Instalación Windows - Learning Agent Web

## 🪟 Despliegue en Windows (Laboratorio)

### 📋 Prerrequisitos para Windows

1. **Windows 10/11** (64-bit)
2. **Docker Desktop for Windows** instalado
3. **PowerShell** o **Command Prompt**
4. **API Key de OpenAI**

### 🚀 Instalación Paso a Paso

#### 1. Instalar Docker Desktop

```powershell
# Opción 1: Descargar desde https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

# Opción 2: Con Chocolatey (si tienes Chocolatey instalado)
choco install docker-desktop

# Opción 3: Con Winget (Windows 11)
winget install Docker.DockerDesktop
```

**⚠️ Importante:** Después de instalar, **reinicia Windows** y abre Docker Desktop para completar la configuración.

#### 2. Verificar Instalación Docker

```powershell
# Abrir PowerShell como Administrador y verificar
docker --version
docker-compose --version
```

#### 3. Preparar el Proyecto

```powershell
# Navegar al directorio del proyecto
cd C:\ruta\al\learning_agent_web

# O si lo tienes en otra ubicación:
cd "C:\Users\TuUsuario\Documents\learning_agent_web"
```

#### 4. Configurar Variables de Entorno

```powershell
# Crear archivo .env.docker con PowerShell
@"
OPENAI_API_KEY=tu-api-key-de-openai-aqui
COMPOSE_PROJECT_NAME=learning-agent-lab
LEARNING_AGENT_PORT=8000
DEBUG_MODE=true
REDIS_PORT=6379
"@ | Out-File -FilePath ".env.docker" -Encoding UTF8
```

#### 5. Desplegar con Script Automático

**Opción A: Script de PowerShell (recomendado)**

```powershell
# Ejecutar el script de PowerShell
.\deploy-lab.ps1
```

**Opción B: Comandos manuales**

```powershell
# Crear directorios
New-Item -ItemType Directory -Force -Path "data", "logs"

# Construir e iniciar
docker-compose --env-file .env.docker up -d --build

# Verificar estado
docker-compose --env-file .env.docker ps

# Verificar que funciona
curl http://localhost:8000/api/mcp/health
```

### 🛠️ Script de PowerShell Automático

```powershell
# deploy-lab.ps1
Write-Host "🚀 Desplegando Learning Agent Web en Windows..." -ForegroundColor Green

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar archivo .env.docker
if (-not (Test-Path ".env.docker")) {
    Write-Host "⚠️ Creando archivo .env.docker..." -ForegroundColor Yellow
    @"
OPENAI_API_KEY=tu-api-key-aqui
COMPOSE_PROJECT_NAME=learning-agent-lab
LEARNING_AGENT_PORT=8000
DEBUG_MODE=true
"@ | Out-File -FilePath ".env.docker" -Encoding UTF8
    Write-Host "⚠️ IMPORTANTE: Configura tu OPENAI_API_KEY en .env.docker" -ForegroundColor Yellow
    exit 1
}

# Crear directorios
Write-Host "📁 Creando directorios..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "data", "logs" | Out-Null

# Detener contenedores existentes
Write-Host "🛑 Deteniendo contenedores existentes..." -ForegroundColor Cyan
docker-compose --env-file .env.docker down 2>$null

# Construir e iniciar
Write-Host "🔨 Construyendo e iniciando servicios..." -ForegroundColor Cyan
docker-compose --env-file .env.docker up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 ¡Despliegue completado exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Accesos disponibles:" -ForegroundColor White
    Write-Host "   • Aplicación: http://localhost:8000" -ForegroundColor White
    Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   • Chat: http://localhost:8000/chat" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Comandos útiles:" -ForegroundColor White
    Write-Host "   • Ver logs: docker-compose --env-file .env.docker logs -f" -ForegroundColor White
    Write-Host "   • Detener: docker-compose --env-file .env.docker down" -ForegroundColor White
    Write-Host "   • Estado: docker-compose --env-file .env.docker ps" -ForegroundColor White
} else {
    Write-Host "❌ Error en el despliegue" -ForegroundColor Red
    exit 1
}
```

### 🎯 Comandos Útiles para Windows

#### PowerShell
```powershell
# Ver logs
docker-compose --env-file .env.docker logs -f

# Reiniciar
docker-compose --env-file .env.docker restart

# Detener
docker-compose --env-file .env.docker down

# Estado de contenedores
docker-compose --env-file .env.docker ps

# Abrir en navegador
start http://localhost:8000
```

#### Command Prompt (CMD)
```cmd
REM Ver logs
docker-compose --env-file .env.docker logs -f

REM Reiniciar
docker-compose --env-file .env.docker restart

REM Detener
docker-compose --env-file .env.docker down

REM Abrir en navegador
start http://localhost:8000
```

### 🚨 Problemas Comunes en Windows

#### Error: "Docker daemon not running"
```powershell
# Solución: Abrir Docker Desktop y esperar a que inicie
# Verificar en la bandeja del sistema que Docker esté activo
```

#### Error: "Port 8000 already in use"
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar proceso si es necesario (cambiar PID)
taskkill /PID 1234 /F

# O cambiar puerto en docker-compose.yml
# ports: - "8001:8000"
```

#### Error: "Permission denied" o "Access denied"
```powershell
# Ejecutar PowerShell como Administrador
# Clic derecho en PowerShell > "Ejecutar como administrador"
```

#### Error: "Execution Policy"
```powershell
# Cambiar política de ejecución temporalmente
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ejecutar script
.\deploy-lab.ps1

# Restaurar política (opcional)
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
```

### 📁 Estructura de Archivos en Windows

```
C:\learning_agent_web\
├── .env.docker              # Variables de entorno
├── deploy-lab.ps1           # Script de PowerShell
├── docker-compose.yml       # Configuración Docker
├── Dockerfile              # Imagen personalizada
├── data\                   # Datos persistentes
├── logs\                   # Logs de la aplicación
└── backend\                # Código fuente
    ├── app\
    ├── templates\
    └── requirements.txt
```

### 🎯 URLs de Acceso (iguales que en Mac/Linux)

- **🏠 Aplicación**: http://localhost:8000
- **💬 Chat**: http://localhost:8000/chat  
- **📊 Dashboard**: http://localhost:8000/dashboard
- **🛠️ MCP Tools**: http://localhost:8000/mcp-tools
- **📚 API Docs**: http://localhost:8000/docs

### 💡 Consejos para Windows

1. **Usar PowerShell ISE** o **Windows Terminal** para mejor experiencia
2. **Ejecutar como Administrador** si hay problemas de permisos
3. **Verificar Windows Defender** - puede bloquear Docker temporalmente
4. **Usar rutas absolutas** cuando sea posible: `C:\ruta\completa\`
5. **Mantener Docker Desktop actualizado**

### 🔄 Script de Desinstalación (opcional)

```powershell
# uninstall-lab.ps1
Write-Host "🗑️ Desinstalando Learning Agent..." -ForegroundColor Yellow

# Detener y eliminar contenedores
docker-compose --env-file .env.docker down --volumes --remove-orphans

# Eliminar imágenes
docker rmi learning-agent-lab_learning-agent 2>$null
docker rmi redis:7-alpine 2>$null

# Limpiar volúmenes huérfanos
docker volume prune -f

Write-Host "✅ Desinstalación completada" -ForegroundColor Green
```

---

## 🎉 Resumen para Windows

El proceso en Windows es prácticamente idéntico al de Mac/Linux, solo cambian:

1. **Instalación de Docker**: Usar Docker Desktop for Windows
2. **Terminal**: PowerShell en lugar de Bash/Zsh  
3. **Scripts**: `.ps1` en lugar de `.sh`
4. **Permisos**: Ejecutar como Administrador si es necesario

**¡El resto funciona exactamente igual!** 🚀
