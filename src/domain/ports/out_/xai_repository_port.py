from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.explicacion import Explicacion


class XaiRepositoryPort(ABC):
    @abstractmethod
    async def save(self, explicacion: Explicacion) -> Explicacion: ...
    @abstractmethod
    async def find_by_recomendacion(
        self, recomendacion_id: UUID
    ) -> Explicacion | None: ...
