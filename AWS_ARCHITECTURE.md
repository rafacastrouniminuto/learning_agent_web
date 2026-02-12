# Arquitectura AWS - Learning Agent Web
## Despliegue Mínimo con AWS Bedrock
Estimamos 100 usuarios piloto y aproximadamente una escalada de hasta 1000 usuarios (variable en relación a demanda de los servicios living lab) entrando a producción.

También si creen que la arquitectura puede simplificarse no duden en comentarnos.

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INTERNET / USUARIOS                          │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS ROUTE 53 (DNS)                            │
│                      livinglab360.uniminuto.edu                    │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│            CLOUDFRONT (CDN + HTTPS + Cache estático)                 │
│                    SSL/TLS Certificate Manager                       │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  APPLICATION LOAD BALANCER (ALB)                     │
│                      Health Checks + HTTPS                           │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           AWS ECS FARGATE                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Learning Agent Container (FastAPI + Python 3.11)             │  │
│  │  • 0.5 vCPU / 1 GB RAM (mínimo)                              │  │
│  │  • 1-3 tasks (auto-scaling)                                   │  │
│  │  • Puerto 8000                                                │  │
│  │  • Health check: /api/mcp/health                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└───────┬─────────────────────┬──────────────────────┬─────────────────┘
        │                     │                      │
        ▼                     ▼                      ▼
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  RDS MySQL  │    │  ElastiCache     │    │  AWS BEDROCK     │
│  (t3.micro) │    │  Redis           │    │  (Claude 3)      │
│             │    │  (t3.micro)      │    │                  │
│  • Users    │    │  • Sessions      │    │  • Chat AI       │
│  • Paths    │    │  • Cache         │    │  • Embeddings    │
│  • Progress │    │  • Queue         │    │  • Streaming     │
└─────────────┘    └──────────────────┘    └──────────────────┘
        │                     │                      │
        └─────────────────────┴──────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   S3 BUCKET      │
                    │                  │
                    │  • Static files  │
                    │  • Logs          │
                    │  • Backups       │
                    │  • CSV data      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  SECRETS MGR     │
                    │                  │
                    │  • DB password   │
                    │  • JWT secret    │
                    │  • API keys      │
                    └──────────────────┘
```

---

## Componentes de la Arquitectura

### 1. **Compute Layer** - ECS Fargate

**Servicio**: Amazon ECS con AWS Fargate (sin gestión de servidores)

```yaml
Configuración Mínima:
  - CPU: 0.5 vCPU (512)
  - RAM: 1 GB
  - Tasks: 1-3 (auto-scaling)
  - Container: learning-agent-web:latest
  - Registry: Amazon ECR (Elastic Container Registry)
```

**Ventajas**:
- Sin gestión de servidores EC2
- Pago por uso (solo cuando está corriendo)
- Auto-scaling automático
- Integración nativa con ALB

---

### 2. **Load Balancer** - Application Load Balancer (ALB)

```yaml
Configuración:
  - Tipo: Application Load Balancer
  - Listeners: HTTP (80) → HTTPS (443)
  - Target Group: ECS Fargate tasks
  - Health Check: GET /api/mcp/health
```

---

### 3. **Database** - Amazon RDS MySQL

```yaml
Configuración Mínima:
  - Instance: db.t3.micro
  - Engine: MySQL 8.0
  - Storage: 20 GB SSD
  - Multi-AZ: No (mínimo) | Sí (producción)
  - Backup: 7 días
```

**Alternativa más económica**: Amazon RDS Aurora Serverless v2
- Escala automáticamente desde 0.5 ACU
- Solo pagas por lo que usas

- RDS MySQL t3.micro
o
- Aurora Serverless v2

---

### 4. **Cache** - ElastiCache Redis

```yaml
Configuración Mínima:
  - Node Type: cache.t3.micro
  - Engine: Redis 7.x
  - Nodes: 1 (mínimo) | 2-3 (replicación)
  - Uso: Session storage, cache de consultas
```

---

### 5. **IA** - AWS Bedrock (Claude 3)
Usar posiblemente Claude Sonnet 4.5 o GPT OSS 120b (costo consistencia)
```yaml
Modelos Disponibles:
  - Claude 3 Sonnet: Balance costo/calidad
  - GPT OSS 120b: costo
  
Características:
  - Streaming de respuestas
  - Function calling (MCP tools)
  - Embeddings para búsqueda semántica
  - Sin gestión de infraestructura
```

---

### 6. **Storage** - Amazon S3

```yaml
Buckets:
  - learning-agent-static: Archivos estáticos (CSS, JS, imágenes)
  - learning-agent-data: CSVs, backups
  - learning-agent-logs: Logs de aplicación
  
Configuración:
  - Versioning: Habilitado
  - Lifecycle: Mover a Glacier después de 90 días
  - Encryption: AES-256
```

---

### 7. **Secrets Management** - AWS Secrets Manager

```yaml
Secrets Almacenados:
  - DB_PASSWORD: Password de RDS
  - JWT_SECRET_KEY: Para tokens JWT
  - REDIS_PASSWORD: Password de Redis (opcional)
```

**Alternativa**: AWS Systems Manager Parameter Store (gratis hasta 10,000 parámetros)

---

### 8. **CDN** - CloudFront

```yaml
Configuración:
  - Origin: ALB
  - Cache Behavior: Cache archivos estáticos
  - SSL/TLS: AWS Certificate Manager (gratis)
  - Gzip Compression: Habilitado
```

---

### 9. **DNS** - Route 53
REVISAR
```yaml
Configuración:
  - Hosted Zone: uniminuto.edu
  - Hosted Zone: 
  - Record: learning-agent.uniminuto.edu → CloudFront
```

---
