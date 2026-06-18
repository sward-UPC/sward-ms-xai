from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.alerta_academica import AlertaAcademica
from src.domain.entities.explicacion import Explicacion


class XaiRepositoryPort(ABC):
    @abstractmethod
    async def save(self, explicacion: Explicacion) -> Explicacion: ...
    @abstractmethod
    async def find_by_recomendacion(
        self, recomendacion_id: UUID
    ) -> Explicacion | None: ...
    @abstractmethod
    async def find_alertas_por_curso(self, curso_id: UUID) -> list[AlertaAcademica]: ...
