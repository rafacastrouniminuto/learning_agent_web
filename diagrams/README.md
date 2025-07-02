# Diagramas del Sistema Learning Agent Web

Esta carpeta contiene los diagramas técnicos que documentan la arquitectura y funcionamiento del sistema Learning Agent Web del Living Lab UNIMINUTO.

## 📁 Archivos de Diagramas

Cada diagrama está disponible en dos formatos:
- **`.drawio`** - Archivo editable para Draw.io
- **`.png`** - Imagen PNG para visualización rápida

### 1. 🏗️ `architecture_overview`
**Diagrama de Arquitectura General**
- **Archivos:** `architecture_overview.drawio` | `architecture_overview.png`
- **Descripción:** Vista completa de la arquitectura del sistema en capas
- **Componentes:** Frontend, API Layer, Services Layer, Data Layer
- **Tecnologías:** FastAPI, Jinja2, SQLite, OpenAI API, MCP SDK
- **Propósito:** Entender la estructura general y flujo de datos

### 2. 🗄️ `database_schema`
**Esquema de Base de Datos**
- **Archivos:** `database_schema.drawio` | `database_schema.png`
- **Descripción:** Estructura de la base de datos SQLite
- **Tablas:** Users, Learning_Paths
- **Fuentes de datos:** CSV files, External APIs
- **Relaciones:** One-to-Many (Users → Learning Paths)
- **Propósito:** Documentar el modelo de datos y relaciones

### 3. 💬 `chat_flow`
**Flujo del Chat IA**
- **Archivos:** `chat_flow.drawio` | `chat_flow.png`
- **Descripción:** Proceso completo de manejo de conversaciones con IA
- **Componentes:** Autenticación, Parsing, OpenAI Service, Streaming
- **Modos:** General y Learning Path
- **Propósito:** Entender el flujo de mensajes y generación de respuestas

### 4. 🔌 `mcp_components`
**Arquitectura MCP (Model Context Protocol)**
- **Archivos:** `mcp_components.drawio` | `mcp_components.png`
- **Descripción:** Integración del SDK FastMCP y herramientas disponibles
- **Herramientas:** Búsqueda, Accesibilidad, Módulos de aprendizaje
- **Endpoints:** APIs específicas de MCP
- **Propósito:** Documentar la integración y funcionalidades MCP

### 5. 🔐 `auth_flow`
**Flujo de Autenticación JWT**
- **Archivos:** `auth_flow.drawio` | `auth_flow.png`
- **Descripción:** Proceso completo de autenticación y autorización
- **Componentes:** Login, Registro, Validación de tokens, Rutas protegidas
- **Seguridad:** JWT, bcrypt, validaciones
- **Propósito:** Entender el sistema de seguridad implementado

## 🛠️ Cómo visualizar los diagramas

### 📸 **Visualización Rápida (Recomendado)**
Las imágenes PNG están listas para visualización inmediata:
- Abrir directamente los archivos `.png` en cualquier visor de imágenes
- Visualizar en GitHub, navegadores web, o editores de código
- Compartir fácilmente en documentos o presentaciones

### ✏️ **Edición Avanzada**

#### Opción 1: Draw.io Online
1. Ir a [app.diagrams.net](https://app.diagrams.net)
2. Hacer clic en "Open Existing Diagram"
3. Seleccionar el archivo `.drawio` deseado
4. Editar y exportar según necesidad

#### Opción 2: Draw.io Desktop
1. Descargar [Draw.io Desktop](https://github.com/jgraph/drawio-desktop/releases)
2. Instalar la aplicación
3. Abrir el archivo `.drawio` directamente

#### Opción 3: VS Code Extension
1. Instalar la extensión "Draw.io Integration"
2. Abrir el archivo `.drawio` en VS Code
3. Editar directamente en el editor

### 🔄 **Regenerar Imágenes PNG**
Si modificas los archivos `.drawio`, puedes regenerar las imágenes PNG:
```bash
python generate_diagrams_simple.py
```

**Dependencias requeridas:**
```bash
pip install diagrams graphviz pillow
```

**Nota:** En macOS también necesitas instalar Graphviz:
```bash
brew install graphviz
```

## 📊 Información de los Diagramas

| Diagrama | Formatos Disponibles | Última Actualización | Versión | Complejidad |
|----------|---------------------|---------------------|---------|-------------|
| Architecture Overview | `.drawio` `.png` | 2025-07-02 | 1.0 | Media |
| Database Schema | `.drawio` `.png` | 2025-07-02 | 1.0 | Baja |
| Chat Flow | `.drawio` `.png` | 2025-07-02 | 1.0 | Alta |
| MCP Components | `.drawio` `.png` | 2025-07-02 | 1.0 | Media |
| Auth Flow | `.drawio` `.png` | 2025-07-02 | 1.0 | Media |

### 📁 Estructura de Archivos
```
diagrams/
├── README.md                        # Este archivo
├── generate_diagrams_simple.py      # Script para generar PNGs
├── architecture_overview.drawio     # Arquitectura general (editable)
├── architecture_overview.png        # Arquitectura general (imagen)
├── database_schema.drawio           # Esquema BD (editable)  
├── database_schema.png              # Esquema BD (imagen)
├── chat_flow.drawio                 # Flujo chat (editable)
├── chat_flow.png                    # Flujo chat (imagen)
├── mcp_components.drawio            # Componentes MCP (editable)
├── mcp_components.png               # Componentes MCP (imagen)
├── auth_flow.drawio                 # Flujo auth (editable)
└── auth_flow.png                    # Flujo auth (imagen)
```

## 🎯 Propósito de la Documentación

Estos diagramas sirven para:

- **Onboarding de desarrolladores:** Entender rápidamente la arquitectura
- **Documentación técnica:** Referencia para mantenimiento y expansión
- **Revisiones de código:** Validar que las implementaciones sigan la arquitectura
- **Planificación:** Base para nuevas funcionalidades y mejoras
- **Comunicación:** Explicar el sistema a stakeholders técnicos y no técnicos

## 🔄 Mantenimiento

Los diagramas deben actualizarse cuando:
- Se agreguen nuevos componentes al sistema
- Se modifique la estructura de la base de datos
- Se implementen nuevas APIs o endpoints
- Se cambien los flujos de autenticación o chat
- Se agreguen nuevas herramientas MCP

## 📝 Convenciones

- **Colores:** Cada capa/tipo de componente tiene un color específico
- **Iconos:** Uso consistente de emojis para identificar tipos de elementos
- **Flujos:** Flechas indican dirección de datos/control
- **Agrupación:** Contenedores delimitan responsabilidades lógicas

## 🤝 Contribución

Para modificar o agregar diagramas:
1. Usar Draw.io para mantener consistencia
2. Seguir las convenciones de colores y estilos existentes
3. Actualizar este README con nuevos diagramas
4. Incluir fecha de modificación en el diagrama

## 🔧 Regenerar Imágenes PNG

Para regenerar las imágenes PNG automáticamente:

```bash
# Instalar dependencias (si no están instaladas)
pip install diagrams

# Ejecutar script de generación
python generate_simple_diagrams.py
```

El script `generate_simple_diagrams.py` utiliza la librería [diagrams](https://diagrams.mingrammer.com/) de Python para generar imágenes PNG con iconos apropiados y mejor calidad visual.

---

*Generado como parte del proyecto Learning Agent Web - Living Lab UNIMINUTO*
