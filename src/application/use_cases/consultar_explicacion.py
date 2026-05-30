from dataclasses import dataclass
from uuid import UUID

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
            return _from_dict(cacheada)

        explicacion = await self._repo.find_by_recomendacion(cmd.recomendacion_id)
        if explicacion is not None:
            await self._cache.set_explicacion(
                cmd.recomendacion_id, _to_dict(explicacion), self._cache_ttl
            )
        return explicacion


def _to_dict(e: Explicacion) -> dict:
    return {
        "id": str(e.id),
        "recomendacion_id": str(e.recomendacion_id),
        "resumen": e.resumen,
        "detalle": e.detalle,
        "evidencias": [
            {"tipo": ev.tipo, "descripcion": ev.descripcion, "impacto": ev.impacto}
            for ev in e.evidencias
        ],
        "fecha_generacion": e.fecha_generacion.isoformat(),
    }


def _from_dict(d: dict) -> Explicacion:
    from datetime import datetime
    from uuid import UUID as _UUID

    from src.domain.entities.explicacion import EvidenciaExplicativa

    return Explicacion(
        id=_UUID(d["id"]),
        recomendacion_id=_UUID(d["recomendacion_id"]),
        resumen=d["resumen"],
        detalle=d["detalle"],
        evidencias=[EvidenciaExplicativa(**ev) for ev in d.get("evidencias", [])],
        fecha_generacion=datetime.fromisoformat(d["fecha_generacion"]),
    )
