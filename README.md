# Learning Agent Web - Living Lab UNIMINUTO

## 📋 Descripción

Sistema web inteligente del Living Lab UNIMINUTO que utiliza IA para crear rutas de aprendizaje personalizadas. La aplicación combina FastAPI en el backend con un chat conversacional que analiza el perfil del estudiante y genera recomendaciones educativas basadas en módulos STEM+ predefinidos.

## ✨ Características Principales

- **🔐 Autenticación Completa**: Sistema de registro e inicio de sesión con JWT
- **💬 Chat Inteligente con IA**: Interfaz conversacional con streaming en tiempo real usando OpenAI
- **📊 Dashboard Interactivo**: Panel principal con menú lateral ocultable y cards de acción
- **🎯 Generación de Rutas Personalizadas**: Sistema que evalúa perfil y genera rutas basadas en CSV de módulos
- **📚 Gestión de Rutas de Aprendizaje**: Visualización dinámica de rutas generadas con progreso
- **🎨 Diseño Moderno**: Interfaz responsive basada en la paleta de colores del Living Lab
- **⚡ Streaming en Tiempo Real**: Respuestas del chat que se muestran progresivamente
- **📱 Totalmente Responsive**: Optimizado para desktop, tablet y móvil
- **🔧 Model Context Protocol (MCP)**: Integración oficial con FastMCP SDK para herramientas de IA
- **🛠️ Herramientas MCP Disponibles**: Búsqueda de módulos, ejes temáticos, creación de rutas personalizadas

## 🏗️ Arquitectura del Sistema

```
learning_agent_web/
├── backend/
│   ├── app/
│   │   ├── api/                    # Endpoints de la API
│   │   │   ├── auth.py            # Autenticación y registro
│   │   │   └── chat.py            # Chat con streaming y rutas
│   │   ├── core/                  # Configuración y utilidades
│   │   │   ├── config.py          # Variables de entorno
│   │   │   ├── database.py        # Configuración de BD
│   │   │   └── security.py        # JWT y encriptación
│   │   ├── models/                # Modelos de base de datos
│   │   │   └── user.py            # Modelo de usuario
│   │   ├── services/              # Servicios especializados
│   │   │   ├── openai_service.py  # Integración con OpenAI
│   │   │   ├── prompts.py         # Templates de prompts
│   │   │   ├── learning_path_service.py # Lógica de rutas
│   │   │   └── mcp_service.py     # MCP integration (FastMCP SDK)
│   │   ├── static/                # Archivos estáticos
│   │   │   ├── css/styles.css     # Estilos personalizados
│   │   │   └── js/main.js         # JavaScript interactivo
│   │   └── main.py                # Aplicación principal FastAPI
│   ├── templates/                 # Plantillas HTML Jinja2
│   │   ├── base.html              # Template base
│   │   ├── dashboard.html         # Dashboard principal
│   │   ├── chat.html              # Interfaz de chat
│   │   ├── learning_paths.html    # Visualización de rutas
│   │   └── auth/                  # Templates de autenticación
│   ├── data/                      # Datos del sistema
│   │   └── learning_modules.csv   # Módulos STEM+ disponibles
│   ├── .env                       # Variables de entorno
│   └── requirements.txt           # Dependencias Python
```

## 🚀 Instalación y Configuración

### 🐳 Opción 1: Despliegue con Docker (RECOMENDADO para laboratorio)

#### Prerrequisitos
- Docker Desktop instalado
- Clave de API de OpenAI

#### 🍎 Para Mac/Linux

**Instalación Rápida:**
```bash
# 1. Clonar o navegar al proyecto
cd learning_agent_web

# 2. Configurar variables de entorno
cp .env.docker .env.docker.local
# Editar .env.docker.local con tu OPENAI_API_KEY

# 3. Desplegar con un solo comando
./deploy-lab.sh
```

**Comandos Docker Útiles:**
```bash
# Ver logs en tiempo real
docker-compose --env-file .env.docker logs -f

# Reiniciar servicios
docker-compose --env-file .env.docker restart

# Detener servicios
docker-compose --env-file .env.docker down

# Ver estado
docker-compose --env-file .env.docker ps
```

---

### 🪟 Opción 2: Despliegue en Windows

#### Prerrequisitos para Windows
- Windows 10/11 (64-bit)
- Docker Desktop for Windows instalado
- PowerShell o Command Prompt
- Clave de API de OpenAI

#### Instalación Docker Desktop en Windows

```powershell
# Opción 1: Descargar desde https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

# Opción 2: Con Chocolatey (si tienes Chocolatey instalado)
choco install docker-desktop

# Opción 3: Con Winget (Windows 11)
winget install Docker.DockerDesktop
```

**⚠️ Importante:** Después de instalar, **reinicia Windows** y abre Docker Desktop para completar la configuración.

#### Despliegue con Scripts Automáticos

**Opción A: PowerShell (recomendado)**
```powershell
# 1. Configurar variables de entorno
@"
OPENAI_API_KEY=tu-api-key-de-openai-aqui
COMPOSE_PROJECT_NAME=learning-agent-lab
LEARNING_AGENT_PORT=8000
DEBUG_MODE=true
"@ | Out-File -FilePath ".env.docker" -Encoding UTF8

# 2. Ejecutar script de despliegue
.\deploy-lab.ps1
```

**Opción B: Command Prompt (CMD)**
```cmd
REM 1. Configurar API key manualmente en .env.docker
REM 2. Ejecutar script
deploy-lab.bat
```

#### Comandos Útiles para Windows

**PowerShell:**
```powershell
# Ver logs en tiempo real
docker-compose --env-file .env.docker logs -f

# Reiniciar servicios
docker-compose --env-file .env.docker restart

# Detener servicios
docker-compose --env-file .env.docker down

# Ver estado
docker-compose --env-file .env.docker ps

# Abrir en navegador
start http://localhost:8000
```

**Command Prompt:**
```cmd
REM Ver logs
docker-compose --env-file .env.docker logs -f

REM Reiniciar
docker-compose --env-file .env.docker restart

REM Detener
docker-compose --env-file .env.docker down

REM Abrir navegador
start http://localhost:8000
```

#### Solución de Problemas Windows

**Error: "Docker daemon not running"**
```powershell
# Solución: Abrir Docker Desktop y esperar a que inicie
# Verificar en la bandeja del sistema que Docker esté activo
```

**Error: "Execution Policy"**
```powershell
# Cambiar política de ejecución temporalmente
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy-lab.ps1
```

**Error: "Port 8000 already in use"**
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Cambiar puerto en docker-compose.yml si es necesario
# ports: - "8001:8000"
```

---

### 🐍 Opción 3: Instalación Manual (Desarrollo)

#### Prerrequisitos

- Python 3.8+
- Entorno virtual activado
- Clave de API de OpenAI

#### 1. Configuración del Entorno

```bash
# Activar el entorno virtual
source ../learning_agent_env/bin/activate

# Navegar al directorio del backend
cd learning_agent_web/backend
```

#### 2. Instalación de Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

#### 3. Configuración de Variables de Entorno

```bash
# Crear archivo .env con tu configuración
cat > .env << EOF
# Environment variables
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production-123456789
DATABASE_URL=sqlite:///./learning_agent.db
REDIS_URL=redis://localhost:6379/0

# OpenAI Configuration
OPENAI_API_KEY=tu-api-key-de-openai-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
EOF
```

#### 4. Ejecución del Sistema

```bash
# Asegúrate de estar en el directorio correcto
cd learning_agent_web/backend

# Iniciar el servidor de desarrollo con recarga automática
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# El servidor estará disponible en:
# - Aplicación: http://localhost:8000
# - Documentación API: http://localhost:8000/docs
```

**⚠️ Nota importante**: Asegúrate de tener tu API key de OpenAI configurada en el archivo `.env` antes de iniciar el servidor.

---

## 📊 Comparación de Métodos de Instalación

| Característica | Docker (Mac/Linux) | Docker (Windows) | Manual (Desarrollo) |
|---------------|-------------------|------------------|-------------------|
| **Facilidad de instalación** | ⭐⭐⭐⭐⭐ Un comando | ⭐⭐⭐⭐⭐ Un comando | ⭐⭐⭐ Varios pasos |
| **Consistencia** | ⭐⭐⭐⭐⭐ Total | ⭐⭐⭐⭐⭐ Total | ⭐⭐ Depende del sistema |
| **Aislamiento** | ⭐⭐⭐⭐⭐ Completo | ⭐⭐⭐⭐⭐ Completo | ⭐ Ninguno |
| **Mantenimiento** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Manual |
| **Para laboratorio** | ✅ Ideal | ✅ Ideal | ❌ No recomendado |
| **Para desarrollo** | ✅ Bueno | ✅ Bueno | ✅ Ideal |

### 🎯 Recomendaciones por Uso

- **🏭 Laboratorio/Producción**: Docker (cualquier OS)
- **💻 Desarrollo local**: Docker o Manual según preferencia
- **🚀 Despliegue rápido**: Docker con scripts automáticos
- **🔧 Debugging intensivo**: Manual para acceso directo al código

---

### 5. Acceso a la Aplicación

- **URL Principal**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **API Alternativa**: http://localhost:8000/redoc

## 💻 Comandos de Desarrollo

### Comandos Básicos

```bash
# Navegar al directorio del backend (IMPORTANTE)
cd learning_agent_web/backend

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload

# Iniciar en modo debug con logs detallados
uvicorn app.main:app --reload --log-level debug

# Iniciar en puerto específico
uvicorn app.main:app --reload --port 8080

# Iniciar accesible desde red externa
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verificar sintaxis Python
python -m py_compile app/main.py

# Instalar nueva dependencia
pip install nueva-dependencia
pip freeze > requirements.txt

# Verificar que el entorno virtual está activo
which python  # Debe mostrar la ruta del entorno virtual
```

### Comandos de Base de Datos

```bash
# Crear base de datos (automático al iniciar)
# Las tablas se crean automáticamente con SQLAlchemy

# Resetear base de datos (eliminar archivo SQLite)
rm learning_agent.db

# Comandos específicos para MCP
# Verificar estado del servicio MCP
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/mcp/health

# Obtener herramientas MCP disponibles
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/mcp/tools

# Búsqueda de módulos via MCP
curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/api/mcp/modules/search?topic=programacion&limit=5"
```

## 📖 Guía de Uso

### 1. Registro e Inicio de Sesión

1. Accede a http://localhost:8000
2. Crea una cuenta nueva o inicia sesión
3. El sistema te redirigirá al dashboard

### 2. Generación de Rutas de Aprendizaje

1. En el dashboard, haz clic en "Generar Ruta de Aprendizaje" o ve directamente al "Chat con IA"
2. Conversa con el agente sobre tus objetivos educativos
3. El sistema analizará tu perfil y te hará preguntas específicas del pretest
4. Cuando el agente tenga suficiente información, te presentará una ruta recomendada
5. Confirma la ruta y aparecerá el botón "🚀 Generar Ruta de Aprendizaje"
6. Haz clic para confirmar y generar tu ruta personalizada
7. La ruta se guardará y podrás verla en "Rutas de Aprendizaje"

### 3. Visualización de Rutas

1. Ve a "Rutas de Aprendizaje" en el menú lateral
2. Verás tus rutas generadas con:
   - Módulos recomendados
   - Prioridades (Alta/Media/Baja)
   - Duración estimada
   - Justificaciones personalizadas

### 4. Herramientas MCP (Avanzado)

1. Ve a "Herramientas MCP" en el menú lateral o visita http://localhost:8000/mcp-tools
2. Usa las herramientas especializadas para:
   - Buscar módulos específicos por criterios avanzados
   - Crear rutas de aprendizaje personalizadas directamente
   - Analizar tu perfil de usuario
   - Ver todas las herramientas MCP disponibles
3. Ideal para desarrolladores y usuarios avanzados que quieren probar las capacidades del sistema

### 🔧 Configuración Avanzada

#### 📁 Archivos de Despliegue Disponibles

El proyecto incluye scripts de despliegue para diferentes sistemas operativos:

```
learning_agent_web/
├── deploy-lab.sh           # Script para Mac/Linux (Bash)
├── deploy-lab.ps1          # Script para Windows (PowerShell)  
├── deploy-lab.bat          # Script para Windows (CMD)
├── docker-compose.yml      # Configuración Docker
├── Dockerfile             # Imagen personalizada
├── .env.docker            # Variables de entorno para Docker
├── DEPLOYMENT_GUIDE.md     # Guía detallada de despliegue
└── WINDOWS_DEPLOYMENT.md   # Guía específica para Windows
```

#### 🌐 URLs de Acceso (Todos los Sistemas)

Una vez desplegado, estas URLs estarán disponibles independientemente del sistema operativo:

- **🏠 Página Principal**: http://localhost:8000
- **💬 Chat con IA**: http://localhost:8000/chat  
- **📊 Dashboard**: http://localhost:8000/dashboard
- **🛠️ Herramientas MCP**: http://localhost:8000/mcp-tools
- **📚 API Docs**: http://localhost:8000/docs
- **🏥 Health Check**: http://localhost:8000/api/mcp/health

### Model Context Protocol (MCP) - ¡IMPLEMENTADO! 🎉

El sistema ahora incluye una **implementación completa de Model Context Protocol** que permite al agente de IA acceder a herramientas especializadas para mejorar la generación de rutas de aprendizaje.

#### 🛠️ Herramientas MCP Disponibles

1. **`search_learning_modules`**: Búsqueda avanzada de módulos por tema, dificultad y eje temático
2. **`get_available_thematic_axes`**: Obtención de ejes temáticos disponibles en el sistema
3. **`create_personalized_learning_path`**: Creación de rutas personalizadas usando algoritmos avanzados
4. **`analyze_learning_readiness`**: Análisis de preparación del usuario para módulos específicos
5. **`get_user_learning_profile`**: Obtención del perfil de aprendizaje del usuario
6. **`get_learning_path_progress`**: Seguimiento del progreso en rutas de aprendizaje

#### 🚀 Acceso a Herramientas MCP

La aplicación ahora utiliza la **integración oficial de FastMCP SDK (v1.9.4+)** que proporciona:

- **FastMCP Server montado en**: http://localhost:8000/mcp
- **API Health Check**: http://localhost:8000/api/mcp/health
- **Panel de herramientas MCP**: http://localhost:8000/mcp-tools
- **Documentación API**: http://localhost:8000/docs (busca "MCP" en los endpoints)

**Estado actual de herramientas MCP:**
```json
{
  "status": "healthy",
  "server_name": "learning-agent-mcp",
  "official_mcp": true,
  "modules_loaded": 6,
  "tools_available": 4,
  "implementation": "official",
  "tools": [
    "search_learning_modules",
    "get_available_thematic_axes", 
    "create_personalized_learning_path",
    "get_user_learning_profile"
  ]
}
```

#### 📊 Integración con OpenAI

Las herramientas MCP están completamente integradas con OpenAI Function Calling, lo que permite que el agente de IA:
- Ejecute búsquedas automáticas de módulos durante la conversación
- Genere rutas de aprendizaje usando herramientas especializadas
- Analice la preparación del usuario para contenidos específicos
- Proporcione recomendaciones más precisas y contextualizadas

### 🧪 Testing y Troubleshooting

### ✅ Verificar Integración MCP

```bash
# Test rápido de integración MCP
cd learning_agent_web/backend
python -c "
from dotenv import load_dotenv; load_dotenv()
from app.services.mcp_service import mcp_service_instance, MCP_AVAILABLE
print(f'✅ MCP Disponible: {MCP_AVAILABLE}')
print(f'✅ Implementación: {mcp_service_instance[\"server_info\"][\"implementation\"]}')
print(f'✅ Módulos cargados: {mcp_service_instance[\"server_info\"][\"modules_loaded\"]}')
print(f'✅ Herramientas: {mcp_service_instance[\"server_info\"][\"tools_available\"]}')
"

# Test completo con ejemplos
python test_mcp_integration.py

# Test health check del servidor
curl -X GET "http://localhost:8000/api/mcp/health"
```

### 🔧 Comandos de Troubleshooting

```bash
# Verificar versión de MCP
pip show mcp

# Reinstalar dependencias MCP
pip install --upgrade "mcp>=1.9.4"

# Verificar logs del servidor
tail -f logs/learning_agent.log

# Test directo de herramientas
python -c "
from backend.app.services.mcp_service import search_learning_modules
result = search_learning_modules(topic='STEM', limit=3)
print(f'Módulos encontrados: {len(result)}')
"
```

### 🚨 Problemas Comunes

**Error: "mcp.server.fastmcp" module not found**
```bash
pip install --upgrade "mcp>=1.9.4"
```

**Error: "FastMCP" not available**
```bash
# Verificar versión instalada
pip show mcp
# Debe ser >= 1.9.4 para tener FastMCP
```

**Error: No modules loaded**
```bash
# Verificar que existe el archivo CSV
ls -la backend/data/learning_modules.csv
# Verificar permisos de lectura
cat backend/data/learning_modules.csv | head -3
```

# Model Context Protocol
MCP_SERVER_NAME=learning-agent-mcp
MCP_SERVER_VERSION=1.0.0

# Opcional - Redis para caché
REDIS_URL=redis://localhost:6379/0

# Opcional - Base de datos PostgreSQL para producción
# DATABASE_URL=postgresql://user:password@localhost/learning_agent_db
```

### Configuración de Producción

```bash
# Instalar servidor ASGI para producción
pip install gunicorn

# Ejecutar con Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🛠️ Tecnologías Utilizadas

### Backend

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para manejo de base de datos
- **OpenAI API**: Integración con GPT para el chat inteligente
- **Model Context Protocol (MCP)**: Herramientas especializadas para IA
- **Pydantic**: Validación de datos y configuración
- **JWT**: Autenticación segura con tokens
- **bcrypt**: Encriptación de contraseñas

### Frontend

- **HTML5 + CSS3**: Estructura y estilos modernos
- **JavaScript ES6+**: Interactividad y manejo de streaming
- **Fetch API**: Comunicación asíncrona con el backend
- **Server-Sent Events**: Streaming en tiempo real

### Base de Datos

- **SQLite**: Desarrollo y pruebas
- **PostgreSQL**: Recomendado para producción

## 🎨 Paleta de Colores

El diseño utiliza la identidad visual del Living Lab UNIMINUTO:

```css
/* Colores Primarios */
--primary-blue: #1e3a8a;      /* Azul profundo */
--primary-purple: #7c3aed;     /* Morado institucional */
--primary-light-blue: #3b82f6; /* Azul claro */

/* Colores Complementarios */
--accent-cyan: #06b6d4;        /* Cian vibrante */
--accent-pink: #ec4899;        /* Rosa energético */
--accent-yellow: #f59e0b;      /* Amarillo cálido */

/* Gradientes */
--gradient-main: linear-gradient(135deg, var(--primary-purple), var(--accent-cyan));
```

## 📊 Funcionalidades del Sistema

### ✅ Implementadas

- [x] Sistema completo de autenticación con JWT
- [x] Chat conversacional con streaming de OpenAI en tiempo real
- [x] Dashboard interactivo con menú lateral ocultable
- [x] Generación inteligente de rutas basada en CSV de módulos STEM+
- [x] Templates de prompts profesionales encapsulados
- [x] Visualización dinámica de rutas de aprendizaje con tarjetas
- [x] Diseño responsive y moderno con paleta Living Lab
- [x] Área de escritura del chat mejorada (más grande y legible)
- [x] Manejo de errores y logging detallado
- [x] Validación de datos con Pydantic
- [x] Botón dinámico para generar rutas desde el chat
- [x] Persistencia temporal de rutas con sessionStorage
- [x] Interfaz optimizada para desktop y móvil
- [x] **Implementación completa de Model Context Protocol (MCP)**
- [x] **Herramientas MCP para búsqueda y análisis de módulos**
- [x] **Integración MCP con OpenAI Function Calling**
- [x] **API endpoints MCP para desarrollo y testing**
- [x] **Página de herramientas MCP para pruebas y desarrollo**

### 🔄 En Desarrollo

- [ ] Persistencia de conversaciones en base de datos
- [ ] Sistema de progreso y seguimiento de rutas
- [ ] Notificaciones y recordatorios
- [ ] Exportación de rutas en PDF/Excel
- [ ] Sistema de retroalimentación y evaluación
- [ ] Integración con librerías MCP oficiales (migración desde implementación custom)

### 🚀 Futuras Expansiones

- [ ] Integración con LMS institucional
- [ ] Módulos de realidad virtual/aumentada
- [ ] Sistema de gamificación
- [ ] Analytics y métricas de aprendizaje
- [ ] Integración con calendar y planificación
- [ ] Soporte multiidioma
- [ ] MCP Servers especializados para diferentes dominios educativos

## 🔍 Solución de Problemas

### Problemas Comunes

**Error: "OPENAI_API_KEY not found"**
```bash
# Verificar que el archivo .env existe y tiene la API key
cat .env | grep OPENAI_API_KEY
```

**Error de conexión a la base de datos**
```bash
# Eliminar y recrear la base de datos
rm learning_agent.db
# Reiniciar el servidor para que se recree automáticamente
```

**Estilos CSS no se actualizan**
```bash
# Forzar recarga del navegador
# Mac: Cmd + Shift + R
# Windows/Linux: Ctrl + F5
```

**Error de dependencias**
```bash
# Reinstalar todas las dependencias
pip install --force-reinstall -r requirements.txt
```

## 🚨 Troubleshooting Avanzado

### Logs y Debugging

```bash
# Ver logs detallados del servidor
uvicorn app.main:app --reload --log-level debug

# Verificar conexión con OpenAI
python -c "
from app.services.openai_service import openai_service
import asyncio
async def test():
    try:
        response = await openai_service.chat_completion([{'role': 'user', 'content': 'test'}])
        print('✅ OpenAI conectado:', response[:50])
    except Exception as e:
        print('❌ Error OpenAI:', e)
asyncio.run(test())
"

# Verificar carga del CSV
python -c "
from app.services.learning_path_service import learning_path_service
modules = learning_path_service.get_modules_context()
print('✅ Módulos cargados:', len(learning_path_service.modules_data))
print('Primer módulo:', learning_path_service.modules_data[0] if learning_path_service.modules_data else 'No hay módulos')
"
```

### Errores Específicos y Soluciones

**Error: "ModuleNotFoundError: No module named 'app'"**
```bash
# Asegúrate de estar en el directorio correcto
cd learning_agent_web/backend
python -c "import app.main"  # Debe ejecutarse sin error
```

**Error: "CORS policy: No 'Access-Control-Allow-Origin'"**
```bash
# Verificar configuración CORS en app/main.py
grep -n "CORSMiddleware" app/main.py
```

**Chat no recibe respuestas**
```bash
# Verificar API key en logs
grep "Initializing OpenAI" logs/
# O reiniciar servidor y verificar el mensaje inicial
```

**Herramientas MCP no funcionan**
```bash
# Verificar estado MCP
curl http://localhost:8000/api/mcp/health
# Verificar módulos cargados en logs del servidor
grep "MCP: Loaded" logs/
```

**Error: "MCP service not available"**
```bash
# Verificar integración MCP en logs
grep "MCP Integration" logs/
# Reiniciar servidor si es necesario
```

## 📁 Archivos Clave del Sistema

### Configuración Principal

- **`backend/.env`**: Variables de entorno (requiere tu API key de OpenAI)
- **`backend/requirements.txt`**: Dependencias Python actualizadas
- **`backend/app/main.py`**: Aplicación principal FastAPI

### Despliegue Docker

- **`Dockerfile`**: Imagen Docker personalizada con Python 3.11
- **`docker-compose.yml`**: Configuración de servicios (app + Redis)
- **`.env.docker`**: Variables de entorno específicas para Docker
- **`deploy-lab.sh`**: Script automático para Mac/Linux
- **`deploy-lab.ps1`**: Script automático para Windows (PowerShell)
- **`deploy-lab.bat`**: Script automático para Windows (CMD)

### Documentación

- **`DEPLOYMENT_GUIDE.md`**: Guía completa de despliegue para laboratorio
- **`WINDOWS_DEPLOYMENT.md`**: Guía específica para Windows con troubleshooting
- **`README.md`**: Este archivo con toda la documentación

### Datos y Configuración

- **`backend/data/learning_modules.csv`**: Módulos STEM+ disponibles (6 ejes temáticos)
- **`backend/app/services/prompts.py`**: Templates de prompts para el chat IA
- **`backend/app/services/learning_path_service.py`**: Lógica de generación de rutas

### Frontend y Estilos

- **`backend/app/static/css/styles.css`**: Estilos actualizados con mejoras del chat
- **`backend/app/static/js/main.js`**: JavaScript con manejo de streaming y rutas
- **`backend/templates/chat.html`**: Interfaz de chat mejorada
- **`backend/templates/learning_paths.html`**: Visualización de rutas generadas

### APIs y Servicios

- **`backend/app/api/chat.py`**: Endpoint de chat con streaming y generación de rutas
- **`backend/app/services/mcp_service.py`**: Implementación completa del servicio MCP
- **`backend/app/api/mcp.py`**: Endpoints de API para herramientas MCP
- **`backend/templates/mcp_tools.html`**: Página de herramientas MCP para testing
- **`backend/app/integrations.py`**: Configuración de integración MCP con OpenAI
- **`backend/app/services/openai_service.py`**: Integración con OpenAI optimizada

---

## 📝 Notas de Versión

### v1.0.0 (Actual) - Diciembre 2024
- ✅ Sistema base completo con autenticación JWT
- ✅ Chat inteligente con OpenAI streaming en tiempo real
- ✅ Generación de rutas de aprendizaje personalizadas
- ✅ Dashboard moderno y responsive con menú lateral ocultable
- ✅ Integración con CSV de módulos STEM+ (6 ejes temáticos)
- ✅ Templates de prompts profesionales encapsulados
- ✅ Área de chat mejorada (textarea más grande, mejor tipografía)
- ✅ Visualización dinámica de rutas con tarjetas interactivas
- ✅ Sistema de botón dinámico para confirmar generación de rutas
- ✅ Diseño basado en paleta de colores Living Lab UNIMINUTO
- ✅ **Implementación completa de Model Context Protocol (MCP)**
- ✅ **Integración MCP con OpenAI Function Calling**
- ✅ **6 herramientas MCP especializadas para el dominio educativo**
- ✅ **Página de herramientas MCP para testing y desarrollo**
- ✅ **API endpoints MCP completamente funcionales**

### Próximas Versiones
- **v1.1.0**: Persistencia de conversaciones y rutas en BD
- **v1.2.0**: Sistema de progreso y seguimiento de aprendizaje
- **v2.0.0**: Migración a librerías MCP oficiales y MCP Servers externos

---

## 🤝 Contribuidores

- **Living Lab UNIMINUTO** - Concepto y diseño pedagógico
- **Equipo de Desarrollo** - Implementación técnica y arquitectura

---

## 📄 Licencia

Este proyecto está desarrollado para el Living Lab UNIMINUTO como parte de su ecosistema educativo de innovación.

---

**Desarrollado con ❤️ para el Living Lab UNIMINUTO**

*Sistema de Rutas de Aprendizaje Inteligentes - Transformando la educación a través de la IA*

## 🎉 Resumen de la Integración MCP

### ✅ Estado Actual

**COMPLETADO:** La integración del Model Context Protocol (MCP) ha sido exitosamente implementada usando el SDK oficial FastMCP v1.9.4+

**Características Implementadas:**
- ✅ **FastMCP Server**: Servidor oficial MCP montado en `/mcp`
- ✅ **4 Herramientas MCP**: Búsqueda de módulos, ejes temáticos, creación de rutas, perfiles de usuario
- ✅ **6 Módulos STEM+**: Cargados desde CSV con formato optimizado
- ✅ **Integración OpenAI**: Function calling habilitado para herramientas MCP
- ✅ **API Endpoints**: Endpoints RESTful para todas las funcionalidades MCP
- ✅ **Health Monitoring**: Endpoint de salud con métricas del servidor MCP
- ✅ **Fallback Robusto**: Sistema híbrido que funciona con/sin FastMCP

### 🚀 Herramientas MCP Disponibles

1. **`search_learning_modules`**: Buscar módulos por tema, dificultad y eje temático
2. **`get_available_thematic_axes`**: Obtener todos los ejes temáticos disponibles  
3. **`create_personalized_learning_path`**: Crear rutas de aprendizaje personalizadas
4. **`get_user_learning_profile`**: Obtener perfil de aprendizaje del usuario

### 🔗 Endpoints Clave

- **FastMCP Server**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/api/mcp/health`
- **API Documentation**: `http://localhost:8000/docs`
- **Dashboard**: `http://localhost:8000/dashboard`
- **Chat Interface**: `http://localhost:8000/chat`

### 📊 Métricas del Sistema

```json
{
  "status": "healthy",
  "official_mcp": true,
  "modules_loaded": 6,
  "tools_available": 4,
  "implementation": "official"
}
```

### 🎯 Próximos Pasos

1. **Testing en Producción**: Probar integración con Claude Desktop
2. **Métricas Avanzadas**: Implementar logging y monitoring detallado
3. **Herramientas Adicionales**: Agregar más funcionalidades MCP específicas
4. **Optimización**: Mejorar rendimiento y caché de respuestas
5. **UI Improvements**: Mejorar visualización de resultados MCP en tiempo real

---

**📧 Contacto**: Living Lab UNIMINUTO - Desarrollo del Sistema de Agente de Aprendizaje Inteligente
