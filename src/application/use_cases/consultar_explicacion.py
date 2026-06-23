from dataclasses import dataclass
from uuid import UUID

from src.application.use_cases.explicacion_mappers import (
    explicacion_from_dict,
    explicacion_to_dict,
)
from src.domain.entities.explicacion import Explicacion
from src.domain.ports.out_.cache_port import CachePort
from src.domain.ports.out_.xai_repository_port import XaiRepositoryPort


@dataclass
class ConsultarExplicacionCommand:
    recomendacion_id: UUID


class ConsultarExplicacionUseCase:
    """Consulta una explicación priorizando la caché Redis (lectura < 50ms).

    Si no está en caché, recurre al repositorio y cachea el resultado.
    """

    def __init__(
        self,
        repo: XaiRepositoryPort,
        cache: CachePort,
        cache_ttl: int = 3600,
    ):
        self._repo = repo
        self._cache = cache
        self._cache_ttl = cache_ttl

    async def execute(self, cmd: ConsultarExplicacionCommand) -> Explicacion | None:
        cacheada = await self._cache.get_explicacion(cmd.recomendacion_id)
        if cacheada is not None:
            return explicacion_from_dict(cacheada)

        explicacion = await self._repo.find_by_recomendacion(cmd.recomendacion_id)
        if explicacion is not None:
            await self._cache.set_explicacion(
                cmd.recomendacion_id, explicacion_to_dict(explicacion), self._cache_ttl
            )
        return explicacion
