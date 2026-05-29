# sward-ms-xai

Microservicio de Explicabilidad XAI del sistema **SWARD**.  
Genera explicaciones interpretables de las recomendaciones adaptativas: mapas de calor de atención del modelo SAKT y explicaciones en lenguaje natural.

## Arquitectura

Arquitectura **Hexagonal (Ports & Adapters)**:

```
src/
  domain/           # Explicacion, PesoAtencion, EvidenciaExplicativa, VisualizacionXAI, MotorExplicabilidad
  application/      # GenerarExplicacionUseCase, ConsultarExplicacionUseCase
  infrastructure/   # FastAPI routers, XaiPostgresAdapter, RedisAdapter, EventBridgeAdapter
```

## Stack

- Python 3.11 · FastAPI · SQLAlchemy 2.0 · PostgreSQL
- Redis (caché de heatmaps) · matplotlib · seaborn
- boto3 (S3 + EventBridge) · Pydantic v2

## SLA de latencia

- Generación de explicación: < 500 ms
- Consulta desde caché Redis: < 50 ms

## Desarrollo local

```bash
cp .env.example .env
docker compose up -d db redis
alembic upgrade head
uvicorn src.infrastructure.adapters.in_.main:app --reload --port 8006
```

## Tests

```bash
pytest tests/ -v --cov=src
```

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/xai/explain` | Generar explicación XAI |
| GET | `/xai/explain/{recomendacionId}` | Consultar explicación (con caché) |

## Proyecto

**TP202610051** — Universidad Peruana de Ciencias Aplicadas (UPC)  
Taller de Proyecto 1 / 2026
