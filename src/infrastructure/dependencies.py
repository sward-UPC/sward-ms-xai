from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sward_shared.auth import build_require_service_key

from src.application.use_cases.consultar_explicacion import ConsultarExplicacionUseCase
from src.application.use_cases.generar_explicacion import GenerarExplicacionUseCase
from src.domain.services.motor_explicabilidad import MotorExplicabilidad
from src.infrastructure.adapters.out_.eventbridge_adapter import EventBridgeAdapter
from src.infrastructure.adapters.out_.redis_adapter import RedisAdapter
from src.infrastructure.adapters.out_.xai_postgres_adapter import XaiPostgresAdapter
from src.infrastructure.config.settings import settings
from src.infrastructure.db.database import get_session

# Validación s2s: solo ms-recomendacion puede llamar a ms-xai.
require_service_key = build_require_service_key(settings.authorized_service_keys_set)


@lru_cache(maxsize=1)
def get_eventbridge_adapter() -> EventBridgeAdapter:
    return EventBridgeAdapter()


@lru_cache(maxsize=1)
def get_redis_adapter() -> RedisAdapter:
    return RedisAdapter(settings.redis_url)


@lru_cache(maxsize=1)
def get_motor_explicabilidad() -> MotorExplicabilidad:
    return MotorExplicabilidad()


def get_generar_explicacion_uc(
    session: AsyncSession = Depends(get_session),
    cache: RedisAdapter = Depends(get_redis_adapter),
    events: EventBridgeAdapter = Depends(get_eventbridge_adapter),
    motor: MotorExplicabilidad = Depends(get_motor_explicabilidad),
) -> GenerarExplicacionUseCase:
    return GenerarExplicacionUseCase(
        XaiPostgresAdapter(session),
        cache,
        events,
        motor,
        settings.explanation_cache_ttl,
    )


def get_consultar_explicacion_uc(
    session: AsyncSession = Depends(get_session),
    cache: RedisAdapter = Depends(get_redis_adapter),
) -> ConsultarExplicacionUseCase:
    return ConsultarExplicacionUseCase(
        XaiPostgresAdapter(session),
        cache,
        settings.explanation_cache_ttl,
    )
