import json
from uuid import UUID

import redis.asyncio as redis

from src.application.ports.out_.cache_port import CachePort


class RedisAdapter(CachePort):
    """Implementación de CachePort con redis.asyncio. RNF: lectura < 50ms."""

    _PREFIX = "xai:explicacion:"

    def __init__(self, redis_url: str):
        self._client = redis.from_url(redis_url, decode_responses=True)

    def _key(self, recomendacion_id: UUID) -> str:
        return f"{self._PREFIX}{recomendacion_id}"

    async def get_explicacion(self, recomendacion_id: UUID) -> dict | None:
        raw = await self._client.get(self._key(recomendacion_id))
        return json.loads(raw) if raw else None

    async def set_explicacion(
        self, recomendacion_id: UUID, data: dict, ttl: int
    ) -> None:
        await self._client.set(self._key(recomendacion_id), json.dumps(data), ex=ttl)
