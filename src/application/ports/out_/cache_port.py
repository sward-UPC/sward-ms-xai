from abc import ABC, abstractmethod
from uuid import UUID


class CachePort(ABC):
    """Puerto de caché (Redis). RNF: lectura de caché < 50ms."""

    @abstractmethod
    async def get_explicacion(self, recomendacion_id: UUID) -> dict | None: ...
    @abstractmethod
    async def set_explicacion(
        self, recomendacion_id: UUID, data: dict, ttl: int
    ) -> None: ...
