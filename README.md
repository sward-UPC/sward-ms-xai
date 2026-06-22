# sward-ms-xai

Microservicio de **Explicabilidad (XAI)** del sistema **SWARD**.

Su responsabilidad es **explicar las predicciones del modelo SAKT** y **exponer
las alertas de riesgo académico** al dashboard docente:

- Convierte los **pesos de atención** del modelo SAKT en explicaciones
  interpretables (resumen en lenguaje natural + evidencias cuantificadas) sobre
  por qué se recomendó un recurso a un estudiante.
- Persiste y cachea las explicaciones para servirlas con baja latencia.
- Publica el evento `sward.xai.ExplicacionGenerada` para el resto del ecosistema.
- Lee las **alertas de riesgo** que escribe `sward-lambda-alertas` y las sirve al
  panel del docente.

---

## Stack

- **Python 3.11** · **FastAPI** · **Uvicorn**
- **SQLAlchemy 2.0** (async) · **PostgreSQL** · **asyncpg**
- **Redis** (`redis.asyncio`) como caché de explicaciones
- **boto3** + **Amazon EventBridge** para eventos de dominio
- **Pydantic v2** / **pydantic-settings** para esquemas y configuración
- **Scalar** para la referencia de API interactiva
- **sward-shared** (librería de contratos compartida de la organización: eventos,
  autenticación s2s/JWT, adaptador EventBridge)
- Tooling: **pytest** · **ruff** · **bandit** · **pip-audit**

---

## Arquitectura hexagonal (Ports & Adapters)

El dominio no conoce FastAPI, SQLAlchemy, Redis ni AWS; los adaptadores de
entrada (`in_`) y salida (`out_`) están separados, y `dependencies.py` es el
único punto que cablea implementaciones concretas a los puertos.

```
src/
  domain/                              # Núcleo: sin frameworks de I/O
    entities/
      explicacion.py                   # Explicacion, PesoAtencion, EvidenciaExplicativa
      alerta_academica.py              # AlertaAcademica (riesgo del estudiante)
      visualizacion_xai.py             # VisualizacionXAI (heatmaps)
    services/
      motor_explicabilidad.py          # Servicio de dominio: pesos SAKT -> texto/evidencias
    events/
      explicacion_generada_event.py    # Evento "sward.xai.ExplicacionGenerada"
    ports/out_/
      xai_repository_port.py           # Persistencia (explicaciones + alertas)
      cache_port.py                    # Caché Redis
      event_publisher_port.py          # Publicación de eventos

  application/
    use_cases/
      generar_explicacion.py           # GenerarExplicacionUseCase (+ command)
      consultar_explicacion.py         # ConsultarExplicacionUseCase (caché primero)
      consultar_alertas.py             # ConsultarAlertasUseCase (dashboard docente)

  infrastructure/
    adapters/in_/                      # Adaptadores de ENTRADA (driving)
      main.py                          # App FastAPI, CORS, security headers, lifespan
      xai_router.py                    # Endpoints /xai/* + esquemas Pydantic
    adapters/out_/                     # Adaptadores de SALIDA (driven)
      xai_postgres_adapter.py          # Implementa XaiRepositoryPort (SQLAlchemy)
      redis_adapter.py                 # Implementa CachePort
      eventbridge_adapter.py           # Implementa EventPublisherPort (EventBridge)
    config/
      settings.py                      # Configuración (pydantic-settings)
    db/
      database.py                      # Engine async + sesión por request
      models/xai_models.py             # ORM: ExplanationModel, AlertModel
    dependencies.py                    # Composition root (FastAPI Depends)

tests/
  unit/                               # Dominio y casos de uso con fakes en memoria
  integration/                        # App in-process con httpx.AsyncClient
```

---

## Endpoints

Base path: `/xai`. Documentación interactiva en `/scalar`; esquema OpenAPI en
`/xai/openapi.json`.

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| `POST` | `/xai/explain` | Genera la explicación de una recomendación a partir de sus pesos de atención SAKT. Persiste, cachea y publica `ExplicacionGenerada`. | Service Key (s2s) |
| `GET` | `/xai/explain/{recomendacion_id}` | Consulta una explicación previamente generada (caché Redis primero, luego BD). | Service Key (s2s) |
| `GET` | `/xai/alerts?courseId={uuid}` | Lista las alertas de riesgo académico de un curso (más recientes primero) para el dashboard docente. | JWT |
| `GET` | `/health` | Sonda de liveness/readiness. | — |

**Autenticación.** Los endpoints de explicaciones se protegen con **service key**
(`X-Service-Key`), pensados para llamadas máquina-a-máquina desde
`sward-ms-recomendacion`. El endpoint de alertas usa **JWT** (token HS256 emitido
por `sward-ms-usuarios`) porque lo consume el frontend del docente.

### Ejemplo — generar explicación

```http
POST /xai/explain
X-Service-Key: <clave-de-servicio>
Content-Type: application/json

{
  "recomendacion_id": "550e8400-e29b-41d4-a716-446655440002",
  "pesos_atencion": [
    { "interaccion_referencia_id": "550e8400-e29b-41d4-a716-446655440003",
      "peso": 0.85, "concepto": "Búsqueda binaria" }
  ]
}
```

Respuesta `201` con `id`, `recomendacion_id`, `resumen`, `detalle`,
`evidencias[]` y `fecha_generacion`.

---

## SLA de latencia

- Generación de explicación (`POST /xai/explain`): objetivo **< 500 ms**
  (en desarrollo el motor no usa LLM, no hay operaciones pesadas).
- Consulta desde caché Redis (`GET /xai/explain/...`): objetivo **< 50 ms**.

---

## Variables de entorno

Ver `.env.example`. Principales:

| Variable | Por defecto | Descripción |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://sward:sward@localhost:5432/xai_db` | Cadena de conexión async a PostgreSQL. |
| `DB_USERNAME` / `DB_PASSWORD` / `DATABASE_HOST` / `DATABASE_PORT` / `DATABASE_NAME` | `""` / `5432` | Componentes inyectados por la task definition de ECS (CDK + Secrets Manager). Si están presentes, recomponen `DATABASE_URL`. |
| `REDIS_URL` | `redis://localhost:6379/0` | Conexión a Redis (caché de explicaciones). |
| `EXPLANATION_CACHE_TTL` | `3600` | TTL en segundos de las explicaciones en caché. |
| `AWS_REGION` | `us-east-1` | Región para EventBridge. |
| `EVENTBRIDGE_BUS_NAME` | `sward-event-bus` | Nombre del event bus de EventBridge. |
| `ENVIRONMENT` | `development` | `development` desactiva HSTS y publica eventos solo por log. |
| `SERVICE_NAME` | `sward-ms-xai` | Identificador del servicio. |
| `CORS_ALLOWED_ORIGINS` | `["http://localhost:5173"]` | Orígenes permitidos para CORS. |
| `SECRET_KEY` | `dev-secret-change-in-production` | Secreto para validar el JWT (HS256). |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de firma del JWT. |
| `SERVICE_KEY` | `""` | Clave que este servicio envía como `X-Service-Key` en llamadas salientes. |
| `AUTHORIZED_SERVICE_KEYS` | `""` | Claves de servicio entrantes autorizadas (separadas por coma). |
| `AUTHORIZED_RECOMENDACION_KEY` | `""` | Clave de `ms-recomendacion`, inyectada por CDK vía Secrets Manager. |

---

## Desarrollo local

```bash
cp .env.example .env

# Levantar dependencias (PostgreSQL 15 + Redis 7)
docker compose up -d db redis

# Instalar dependencias
pip install -r requirements.txt -r requirements-dev.txt

# Arrancar el servicio (crea las tablas en el arranque vía lifespan)
uvicorn src.infrastructure.adapters.in_.main:app --reload --port 8006
```

- API: `http://localhost:8006`
- Docs interactivas (Scalar): `http://localhost:8006/scalar`
- Health: `http://localhost:8006/health`

> El esquema se materializa con `Base.metadata.create_all` en el `lifespan` de la
> app (con reintentos mientras la BD arranca), por lo que no hace falta un paso
> de migración manual en local.

### Levantar todo con Docker Compose

```bash
docker compose up --build
```

El servicio `app` expone el puerto `8006` y depende de `db` y `redis`.

---

## Tests y calidad

```bash
pytest -q                    # suite completa (unit + integration in-process)
pytest --cov=src             # con cobertura
ruff check                   # linting
bandit -r src                # análisis de seguridad estático
pip-audit                    # auditoría de dependencias
```

- **Unitarios** (`tests/unit/`): dominio (`MotorExplicabilidad`) y casos de uso
  con fakes en memoria que cumplen los puertos — sin BD, sin Redis, sin FastAPI.
- **Integración** (`tests/integration/`): la app se ejerce in-process con
  `httpx.AsyncClient` + `ASGITransport` (sin levantar servidor).

---

## Flujo de despliegue

1. **CI** (`.github/workflows/ci.yml`): en cada push/PR a `main` reutiliza el
   workflow de la organización (`sward-UPC/.github` → `ci-microservice.yml`) que
   ejecuta lint (ruff), tests (pytest) y los chequeos de seguridad.
2. **Build & push** (`.github/workflows/build-push.yml`): al hacer push a la rama
   `deploy` reutiliza `build-push-ghcr.yml` de la organización, que construye la
   imagen Docker (`Dockerfile`, base `python:3.11-slim`, usuario no-root, puerto
   `8000`), la publica en **GHCR** y actualiza el servicio `xai` en el cluster
   ECS `sward-cluster`.
3. **Infraestructura (CDK)**: el servicio corre como tarea **ECS Fargate** detrás
   del ALB. La configuración sensible (credenciales de BD, claves de servicio) se
   inyecta como variables de entorno desde **AWS Secrets Manager**; cuando
   `DATABASE_HOST`/`DB_USERNAME` están presentes, `settings.py` recompone
   `DATABASE_URL` automáticamente.
4. En producción (`ENVIRONMENT != development`) se activan las cabeceras de
   seguridad (incluido HSTS) y los eventos `ExplicacionGenerada` se publican
   realmente a **EventBridge** (en `development` solo se registran por log).

---

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)
Taller de Proyecto 1 / 2026.
