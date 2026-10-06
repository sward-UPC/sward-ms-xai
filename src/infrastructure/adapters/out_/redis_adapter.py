"""Caché de explicaciones en Redis.

Es caché pura: la explicación vive en la base, y esto solo evita recalcularla.
Si Redis no responde, se regenera — lo que no puede pasar es que la petición
del estudiante se caiga por ello.

El 5 de octubre de 2026 pasó exactamente eso: POST /xai/explain respondió 500
porque falló el último paso, guardar en caché una explicación que ya estaba
generada y guardada. La excepción revirtió la sesión y la explicación se perdió.
"""

import functools
import json
import logging
from uuid import UUID

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError, TimeoutError as RedisTimeoutError

from src.application.ports.out_.cache_port import CachePort

logger = logging.getLogger(__name__)

# La mayoría de las caídas son la conexión ociosa que el otro extremo cierra y
# que el cliente descubre al escribir. Con reintentos y un ping periódico, eso
# se reconecta solo y no llega a la capa de arriba.
REINTENTOS = 3
CHEQUEO_DE_SALUD_SEGUNDOS = 30


def _degrada_a(valor):
    """Si Redis falla, deja constancia y sigue con el valor indicado.

    Degradar no es callar: cada caída queda registrada con su tipo de error.
    """

    def envoltura(fn):
        @functools.wraps(fn)
        async def interna(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except RedisError as e:
                logger.warning(
                    "Redis no respondió en %s (%s): se continúa sin caché",
                    fn.__name__,
                    type(e).__name__,
                )
                return valor

        return interna

    return envoltura


class RedisAdapter(CachePort):
    """Implementación de CachePort con redis.asyncio. RNF: lectura < 50ms."""

    _PREFIX = "xai:explicacion:"

    def __init__(self, redis_url: str):
        self._client = redis.from_url(
            redis_url,
            decode_responses=True,
            retry=Retry(ExponentialBackoff(cap=0.5, base=0.05), REINTENTOS),
            retry_on_error=[RedisConnectionError, RedisTimeoutError],
            health_check_interval=CHEQUEO_DE_SALUD_SEGUNDOS,
        )

    def _key(self, recomendacion_id: UUID) -> str:
        return f"{self._PREFIX}{recomendacion_id}"

    @_degrada_a(None)
    async def get_explicacion(self, recomendacion_id: UUID) -> dict | None:
        raw = await self._client.get(self._key(recomendacion_id))
        return json.loads(raw) if raw else None

    @_degrada_a(None)
    async def set_explicacion(
        self, recomendacion_id: UUID, data: dict, ttl: int
    ) -> None:
        await self._client.set(self._key(recomendacion_id), json.dumps(data), ex=ttl)
