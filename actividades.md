# Actividades del Proyecto Learning Agent Web

## Timeline de Desarrollo MVP - 6 Semanas

Historias de usuario organizadas por sprints basadas en el desarrollo real del proyecto learning_agent_web.

---

## **Sprint 1 (Semanas 1-2) - Infraestructura Base**

### ✅ **YA REALIZADAS:**

**HU-001: Setup FastAPI**
- **Como** desarrollador
- **Quiero** configurar FastAPI con estructura modular
- **Para** tener una base sólida para el backend
- **Estado:** ✅ Completado
- **Modificaciones:** Configurado con SQLAlchemy, autenticación JWT, CORS, y estructura de APIs modulares

**HU-002: Setup React (Reemplazado por Templates HTML)**
- **Como** desarrollador  
- **Quiero** una interfaz de usuario moderna
- **Para** que los usuarios tengan una experiencia fluida
- **Estado:** ✅ Completado (con modificación)
- **Modificaciones:** Se usó Jinja2 templates + CSS/JS vanilla en lugar de React para mayor simplicidad

**HU-003: Setup DB**
- **Como** desarrollador
- **Quiero** configurar SQLite con SQLAlchemy
- **Para** persistir datos de usuarios y rutas de aprendizaje
- **Estado:** ✅ Completado
- **Modificaciones:** Configurado con modelos User, LearningPath y sistema de migraciones

**HU-004: Auth Básica**
- **Como** usuario
- **Quiero** registrarme e iniciar sesión
- **Para** acceder a funcionalidades personalizadas
- **Estado:** ✅ Completado
- **Modificaciones:** Implementado JWT con endpoints de registro/login y middleware de autenticación

---

## **Sprint 2 (Semanas 3-4) - Core Features**

### ✅ **YA REALIZADAS:**

**HU-005: MCP SDK Setup**
- **Como** desarrollador
- **Quiero** integrar el SDK oficial de Model Context Protocol
- **Para** habilitar herramientas MCP en la aplicación
- **Estado:** ✅ Completado
- **Modificaciones:** Implementado con FastMCP, herramientas de accesibilidad y búsqueda de módulos

**HU-006: Motor Conversacional**
- **Como** usuario
- **Quiero** chatear con un agente IA
- **Para** obtener recomendaciones de aprendizaje personalizadas
- **Estado:** ✅ Completado
- **Modificaciones:** Integrado OpenAI API con streaming, historial de conversación y modo learning_path

**HU-007: Servicio Pretest**
- **Como** usuario
- **Quiero** evaluar mi nivel actual de conocimiento
- **Para** recibir recomendaciones apropiadas
- **Estado:** 🔄 En progreso
- **Modificaciones:** Pendiente de implementar sistema de evaluación inicial

### 🔄 **PENDIENTES:**

**HU-008: MCP Servidor**
- **Como** desarrollador
- **Quiero** un servidor MCP funcional
- **Para** exponer herramientas especializadas de aprendizaje
- **Estado:** 🔄 Parcialmente completado
- **Modificaciones necesarias:** Expandir herramientas MCP más allá de accesibilidad

**HU-009: Cache Setup**
- **Como** desarrollador
- **Quiero** implementar Redis para caché
- **Para** mejorar el rendimiento de la aplicación
- **Estado:** ❌ Pendiente

---

## **Sprint 3 (Semanas 5-6) - Refinamiento & MVP**

### ✅ **YA REALIZADAS:**

**HU-010: OpenAI Integration**
- **Como** usuario
- **Quiero** interactuar con GPT-4
- **Para** recibir asesoramiento educativo inteligente
- **Estado:** ✅ Completado
- **Modificaciones:** Implementado con streaming, manejo de errores y límites de tokens

**HU-011: Generador Rutas**
- **Como** usuario
- **Quiero** generar rutas de aprendizaje personalizadas
- **Para** tener un plan estructurado de estudio
- **Estado:** ✅ Completado
- **Modificaciones:** Integrado en el chat con persistencia en BD y visualización

**HU-012: Router Modelos**
- **Como** desarrollador
- **Quiero** enrutar a diferentes modelos según el contexto
- **Para** optimizar respuestas y costos
- **Estado:** ❌ Pendiente

### 🔄 **PENDIENTES:**

**HU-013: Testing**
- **Como** desarrollador
- **Quiero** tests automatizados completos
- **Para** asegurar la calidad del código
- **Estado:** 🔄 Parcialmente completado
- **Modificaciones:** Se han creado algunos tests de MCP y accesibilidad

---

## **Sprint EXTRA - Funcionalidades Adicionales Implementadas**

### ✅ **COMPLETADAS (No en timeline original):**

**HU-014: Sistema de Accesibilidad**
- **Como** usuario con discapacidad visual
- **Quiero** herramientas de accesibilidad integradas
- **Para** usar la plataforma sin barreras
- **Estado:** ✅ Completado
- **Incluye:** TTS en español, contraste, tamaño de fuente, lector de pantalla, atajos de teclado

**HU-015: Herramientas MCP**
- **Como** usuario
- **Quiero** buscar módulos de aprendizaje
- **Para** encontrar contenido relevante fácilmente
- **Estado:** ✅ Completado
- **Incluye:** API de búsqueda, filtros por dificultad y eje temático

**HU-016: Visita Virtual 3D**
- **Como** usuario
- **Quiero** explorar el Living Lab en 3D
- **Para** conocer el espacio físico virtualmente
- **Estado:** 🔄 En desarrollo
- **Incluye:** Three.js, navegación 3D, recreación del layout del lab

**HU-017: Sistema de Navegación**
- **Como** usuario
- **Quiero** navegar fácilmente entre secciones
- **Para** acceder rápidamente a todas las funcionalidades
- **Estado:** ✅ Completado
- **Incluye:** Sidebar responsivo, breadcrumbs, navegación intuitiva

---

## **Historias Pendientes Sugeridas:**

**HU-018: Dashboard Analytics**
- **Como** usuario
- **Quiero** ver mi progreso de aprendizaje
- **Para** monitorear mi avance
- **Estado:** ❌ Pendiente
- **Prioridad:** Media

**HU-019: Sistema de Notificaciones**
- **Como** usuario
- **Quiero** recibir recordatorios de estudio
- **Para** mantener consistencia en mi aprendizaje
- **Estado:** ❌ Pendiente
- **Prioridad:** Baja

**HU-020: Exportar Rutas de Aprendizaje**
- **Como** usuario
- **Quiero** exportar mis rutas en PDF/JSON
- **Para** usar fuera de la plataforma
- **Estado:** ❌ Pendiente
- **Prioridad:** Media

**HU-021: Sistema de Evaluación**
- **Como** usuario
- **Quiero** realizar evaluaciones de mis conocimientos
- **Para** validar mi progreso
- **Estado:** ❌ Pendiente
- **Prioridad:** Alta

**HU-022: Integración con Plataformas Externas**
- **Como** usuario
- **Quiero** conectar con Coursera, edX, etc.
- **Para** acceder a más recursos de aprendizaje
- **Estado:** ❌ Pendiente
- **Prioridad:** Baja

---

## **Resumen de Estado del Proyecto**

### 📊 **Métricas de Progreso:**
- **Total de Historias:** 22
- **Completadas:** 12 (54.5%)
- **En Progreso:** 3 (13.6%)
- **Pendientes:** 7 (31.8%)

### 🎯 **Funcionalidades Core Completadas:**
- ✅ Autenticación y autorización
- ✅ Chat con IA y generación de rutas
- ✅ Sistema de accesibilidad completo
- ✅ Herramientas MCP básicas
- ✅ Interfaz de usuario moderna
- ✅ Integración con OpenAI

### 🔄 **Próximos Pasos Prioritarios:**
1. Completar visita virtual 3D
2. Implementar sistema de evaluación
3. Agregar dashboard de analytics
4. Expandir herramientas MCP
5. Completar suite de testing

### 📝 **Notas Técnicas:**
- Proyecto basado en FastAPI + SQLAlchemy
- Frontend con Jinja2 templates y JavaScript vanilla
- Integración MCP con FastMCP SDK
- Base de datos SQLite para desarrollo
- Autenticación JWT
- Streaming de respuestas con OpenAI API

---

*Última actualización: 25 de junio de 2025*
*Versión: 1.0*
