#!/bin/bash

# Script de despliegue para Learning Agent Web - Living Lab UNIMINUTO
# Uso: ./deploy-lab.sh

echo "🚀 Desplegando Learning Agent Web en el Laboratorio..."
echo "=================================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para mostrar errores
error_exit() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
    exit 1
}

# Función para mostrar éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar advertencias
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    error_exit "Docker no está instalado. Instálalo desde https://docker.com"
fi

# Verificar si Docker Compose está disponible
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error_exit "Docker Compose no está disponible"
fi

# Usar docker compose o docker-compose según disponibilidad
DOCKER_COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "📋 Verificando requisitos previos..."

# Verificar archivo .env.docker
if [ ! -f ".env.docker" ]; then
    warning "Archivo .env.docker no encontrado. Creando uno por defecto..."
    cp .env.docker.template .env.docker 2>/dev/null || {
        echo "OPENAI_API_KEY=tu-api-key-aqui" > .env.docker
    }
    warning "⚠️  IMPORTANTE: Edita .env.docker con tu API key de OpenAI antes de continuar"
    read -p "¿Has configurado tu OPENAI_API_KEY? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error_exit "Configura tu OPENAI_API_KEY en .env.docker primero"
    fi
fi

# Verificar que la API key no sea la por defecto
if grep -q "tu-api-key-aqui" .env.docker; then
    error_exit "Debes configurar tu OPENAI_API_KEY real en .env.docker"
fi

success "Requisitos verificados"

# Crear directorios necesarios
echo "📁 Creando directorios de datos..."
mkdir -p data logs
success "Directorios creados"

# Detener contenedores existentes si los hay
echo "🛑 Deteniendo contenedores existentes..."
$DOCKER_COMPOSE_CMD --env-file .env.docker down 2>/dev/null
success "Contenedores detenidos"

# Construir las imágenes
echo "🔨 Construyendo imágenes Docker..."
$DOCKER_COMPOSE_CMD --env-file .env.docker build || error_exit "Fallo en la construcción de imágenes"
success "Imágenes construidas"

# Iniciar los servicios
echo "🚀 Iniciando servicios..."
$DOCKER_COMPOSE_CMD --env-file .env.docker up -d || error_exit "Fallo al iniciar servicios"

# Esperar a que la aplicación esté lista
echo "⏳ Esperando a que la aplicación esté lista..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/mcp/health > /dev/null 2>&1; then
        success "Aplicación lista!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 ¡Despliegue completado exitosamente!${NC}"
echo ""
echo "📱 Accesos disponibles:"
echo "   • Aplicación principal: http://localhost:8000"
echo "   • Documentación API: http://localhost:8000/docs"
echo "   • Chat con IA: http://localhost:8000/chat"
echo "   • Dashboard: http://localhost:8000/dashboard"
echo "   • Herramientas MCP: http://localhost:8000/mcp-tools"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs: $DOCKER_COMPOSE_CMD --env-file .env.docker logs -f"
echo "   • Detener: $DOCKER_COMPOSE_CMD --env-file .env.docker down"
echo "   • Reiniciar: $DOCKER_COMPOSE_CMD --env-file .env.docker restart"
echo "   • Estado: $DOCKER_COMPOSE_CMD --env-file .env.docker ps"
echo ""
echo "🏥 Health check:"
curl -s http://localhost:8000/api/mcp/health | python3 -m json.tool 2>/dev/null || echo "Ejecuta: curl http://localhost:8000/api/mcp/health"
echo ""
echo "=================================================="
