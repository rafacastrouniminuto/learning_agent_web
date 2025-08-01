# Guía de Despliegue para Laboratorio - Learning Agent Web

## 🏭 Despliegue en Equipos del Laboratorio

### 📋 Lista de Chequeo Pre-Despliegue

- [ ] **Docker Desktop instalado** en el equipo del laboratorio
- [ ] **API Key de OpenAI** válida y configurada
- [ ] **Acceso a internet** para descargar imágenes Docker
- [ ] **Puerto 8000 disponible** (o cambiar en configuración)
- [ ] **Permisos de administrador** para ejecutar Docker

### 🚀 Proceso de Instalación Simplificado

#### 1. Preparación del Entorno

```bash
# Verificar Docker
docker --version
docker-compose --version

# Clonar/copiar proyecto al equipo
# (o usar USB/red compartida)
```

#### 2. Configuración Rápida

```bash
# Navegar al proyecto
cd learning_agent_web

# Configurar API key (OBLIGATORIO)
echo "OPENAI_API_KEY=sk-proj-..." > .env.docker

# Ejecutar script de despliegue automático
./deploy-lab.sh
```

#### 3. Verificación

```bash
# Verificar que está corriendo
curl http://localhost:8000/api/mcp/health

# Abrir en navegador
# http://localhost:8000
```

### 🔧 Solución de Problemas Comunes

#### Error: "Port 8000 already in use"
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar puerto 8001 externamente
```

#### Error: "OPENAI_API_KEY not configured"
```bash
# Verificar configuración
cat .env.docker | grep OPENAI_API_KEY
# Debe mostrar tu API key real, no "tu-api-key-aqui"
```

#### Error: Docker no responde
```bash
# Reiniciar Docker Desktop
# Verificar recursos disponibles (RAM/CPU)
docker system prune  # Limpiar si es necesario
```

### 📊 Monitoreo y Mantenimiento

#### Comandos de Monitoreo

```bash
# Estado de contenedores
docker-compose --env-file .env.docker ps

# Logs en tiempo real
docker-compose --env-file .env.docker logs -f learning-agent

# Uso de recursos
docker stats learning-agent-web

# Health check manual
curl http://localhost:8000/api/mcp/health | python3 -m json.tool
```

#### Comandos de Mantenimiento

```bash
# Reiniciar aplicación
docker-compose --env-file .env.docker restart learning-agent

# Actualizar aplicación (después de cambios)
docker-compose --env-file .env.docker up -d --build

# Backup de datos
cp -r data/ backup-$(date +%Y%m%d)/

# Limpiar logs antiguos
docker-compose --env-file .env.docker exec learning-agent sh -c "truncate -s 0 /app/logs/*.log"
```

### 🔒 Consideraciones de Seguridad para Laboratorio

#### Variables de Entorno
```bash
# Usar secretos diferentes por equipo
SECRET_KEY=living-lab-equipo-01-$(date +%s)

# Configurar CORS específico si es necesario
CORS_ORIGINS=["http://equipolab01:8000", "http://localhost:8000"]
```

#### Red y Acceso
```bash
# Para acceso desde otros equipos del lab
# Modificar docker-compose.yml:
ports:
  - "0.0.0.0:8000:8000"

# Entonces accesible desde:
# http://IP-DEL-EQUIPO:8000
```

### 📱 URLs de Acceso Importantes

Una vez desplegado, estas URLs estarán disponibles:

- **🏠 Página Principal**: http://localhost:8000
- **💬 Chat con IA**: http://localhost:8000/chat  
- **📊 Dashboard**: http://localhost:8000/dashboard
- **🛠️ Herramientas MCP**: http://localhost:8000/mcp-tools
- **📚 API Docs**: http://localhost:8000/docs
- **🏥 Health Check**: http://localhost:8000/api/mcp/health

### 🎯 Scripts de Automatización

#### Script de inicio automático (opcional)
```bash
#!/bin/bash
# guardar como start-learning-agent.sh

cd /ruta/al/learning_agent_web
docker-compose --env-file .env.docker up -d

echo "Learning Agent iniciado en http://localhost:8000"
```

#### Script de respaldo diario (opcional)
```bash
#!/bin/bash
# guardar como backup-daily.sh

DATE=$(date +%Y%m%d)
cd /ruta/al/learning_agent_web

# Backup de datos
tar -czf "backup-$DATE.tar.gz" data/ logs/

# Mantener solo últimos 7 backups
find . -name "backup-*.tar.gz" -mtime +7 -delete
```

### 📞 Soporte y Troubleshooting

#### Logs Importantes
```bash
# Logs de aplicación
docker-compose --env-file .env.docker logs learning-agent

# Logs específicos de errores
docker-compose --env-file .env.docker logs learning-agent | grep ERROR

# Logs de arranque
docker-compose --env-file .env.docker logs learning-agent | head -50
```

#### Información del Sistema
```bash
# Información del contenedor
docker inspect learning-agent-web

# Recursos utilizados
docker stats --no-stream learning-agent-web

# Red del contenedor
docker network ls
docker network inspect learning-agent_learning-agent-network
```

---

## 🎉 ¡Listo para el Laboratorio!

Con esta configuración Docker, cualquier equipo del laboratorio puede tener el Learning Agent funcionando en minutos, sin configurar Python, dependencias, o preocuparse por conflictos de versiones.

**Contacto**: Living Lab UNIMINUTO - Soporte Técnico Sistema Learning Agent
