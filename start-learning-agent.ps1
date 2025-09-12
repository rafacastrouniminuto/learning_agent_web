# Script para iniciar Learning Agent Web automáticamente
# Living Lab UNIMINUTO - 2025

# Configurar ubicación del proyecto
$ProjectPath = "c:\Users\labin\OneDrive\Documentos\Living_lab\learning_agent_web"

# Función para escribir logs
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] $Message"
    Add-Content -Path "$ProjectPath\logs\startup.log" -Value "[$timestamp] $Message"
}

# Crear directorio de logs si no existe
if (!(Test-Path "$ProjectPath\logs")) {
    New-Item -ItemType Directory -Path "$ProjectPath\logs" -Force
}

Write-Log "🚀 Iniciando Learning Agent Web..."

try {
    # Cambiar al directorio del proyecto
    Set-Location $ProjectPath
    Write-Log "📁 Cambiado al directorio: $ProjectPath"
    
    # Verificar que Docker esté ejecutándose
    $dockerRunning = $false
    $attempts = 0
    $maxAttempts = 30
    
    Write-Log "🐳 Esperando que Docker Desktop esté listo..."
    
    while (-not $dockerRunning -and $attempts -lt $maxAttempts) {
        try {
            docker ps > $null 2>&1
            if ($LASTEXITCODE -eq 0) {
                $dockerRunning = $true
                Write-Log "✅ Docker está ejecutándose"
            } else {
                $attempts++
                Write-Log "⏳ Esperando Docker... ($attempts/$maxAttempts)"
                Start-Sleep -Seconds 10
            }
        } catch {
            $attempts++
            Write-Log "⏳ Esperando Docker... ($attempts/$maxAttempts)"
            Start-Sleep -Seconds 10
        }
    }
    
    if (-not $dockerRunning) {
        Write-Log "❌ Docker no pudo iniciarse después de $maxAttempts intentos"
        exit 1
    }
    
    # Configurar variable de entorno de OpenAI
    $env:OPENAI_API_KEY = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
    Write-Log "🔑 API Key configurado desde variables de entorno del sistema"
    
    # Detener contenedores existentes si están ejecutándose
    Write-Log "🛑 Deteniendo contenedores existentes..."
    docker-compose down 2>&1 | Out-Null
    
    # Iniciar los contenedores
    Write-Log "🚀 Iniciando contenedores de Learning Agent..."
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ Learning Agent Web iniciado correctamente"
        Write-Log "🌐 Aplicación disponible en: http://localhost:8000"
        
        # Opcional: abrir navegador después de unos segundos
        Start-Sleep -Seconds 15
        Write-Log "🌐 Abriendo navegador..."
        Start-Process "http://localhost:8000"
    } else {
        Write-Log "❌ Error al iniciar los contenedores"
        exit 1
    }
    
} catch {
    Write-Log "❌ Error durante el inicio: $($_.Exception.Message)"
    exit 1
}

Write-Log "🎉 Proceso de inicio completado"
