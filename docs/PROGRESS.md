# PROGRESS — sward-ms-xai

## Sprint 5 — 2026-05-30

### Implementado
- [x] Entidades: Explicacion, PesoAtencion, EvidenciaExplicativa, VisualizacionXAI
- [x] Domain Service: MotorExplicabilidad (generar_texto, generar_evidencias) — lógica simple sin LLM en dev
- [x] Evento: ExplicacionGeneradaEvent (event_type "sward.xai.ExplicacionGenerada")
- [x] Puertos out: XaiRepositoryPort, CachePort (Redis), EventPublisherPort
- [x] Use Cases: GenerarExplicacionUseCase, ConsultarExplicacionUseCase (caché primero)
- [x] XaiPostgresAdapter (SQLAlchemy async, tabla `explanations` con serialización JSON)
- [x] RedisAdapter con redis.asyncio (RNF caché < 50ms, TTL configurable)
- [x] EventBridgeAdapter (modo dev = log local)
- [x] Endpoints: POST /xai/explain, GET /xai/explain/{recomendacion_id}, GET /health
- [x] Inyección de dependencias con @lru_cache y FastAPI Depends (routers delgados)
- [x] Settings: redis_url, explanation_cache_ttl=3600; servicio en puerto 8006
- [x] Docker Compose: PostgreSQL 15 + Redis 7 (6381:6379)
- [x] Tests unitarios: 5 tests (MotorExplicabilidad x2, GenerarExplicacion, ConsultarExplicacion x2)
- [x] GitHub Actions CI

### Requisitos cubiertos
- RF-004-05: GenerarExplicacionUseCase con latencia objetivo < 500ms (sin operaciones pesadas en dev)
- RNF caché Redis < 50ms: ConsultarExplicacion consulta primero la caché
