"""Mappers entre la entidad ``Explicacion`` y su representación plana de caché.

Estos *mappers* viven en la capa de aplicación porque traducen entre el modelo
de dominio y el formato de persistencia en caché (dict serializable) que usan
varios casos de uso. Se centralizan aquí para evitar duplicación.
"""

from datetime import datetime
from uuid import UUID

from src.domain.entities.explicacion import EvidenciaExplicativa, Explicacion


def explicacion_to_dict(e: Explicacion) -> dict:
    """Convierte una ``Explicacion`` a un dict plano serializable para caché."""
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


def explicacion_from_dict(d: dict) -> Explicacion:
    """Reconstruye una ``Explicacion`` desde su representación plana de caché."""
    return Explicacion(
        id=UUID(d["id"]),
        recomendacion_id=UUID(d["recomendacion_id"]),
        resumen=d["resumen"],
        detalle=d["detalle"],
        evidencias=[EvidenciaExplicativa(**ev) for ev in d.get("evidencias", [])],
        fecha_generacion=datetime.fromisoformat(d["fecha_generacion"]),
    )
