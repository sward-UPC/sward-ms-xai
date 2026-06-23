"""Serializers/helpers de mapeo del adaptador de entrada HTTP.

Traducen entidades del dominio a las estructuras de respuesta que devuelven los
handlers, manteniendo las rutas delgadas.
"""

from src.domain.entities.alerta_academica import AlertaAcademica
from src.domain.entities.explicacion import Explicacion
from src.infrastructure.adapters.in_.schemas import (
    AlertaResponse,
    ConsultarExplicacionResponse,
    EvidenciaResponse,
    ExplicacionResponse,
)


def _evidencias(e: Explicacion) -> list[EvidenciaResponse]:
    return [
        EvidenciaResponse(
            tipo=ev.tipo,
            descripcion=ev.descripcion,
            impacto=ev.impacto,
        )
        for ev in e.evidencias
    ]


def serializar_alerta(a: AlertaAcademica) -> AlertaResponse:
    """Serializa una entidad ``AlertaAcademica`` a modelo de respuesta API."""
    return AlertaResponse(
        id=str(a.id),
        estudiante_id=str(a.estudiante_id),
        curso_id=str(a.curso_id),
        nivel_riesgo=a.nivel_riesgo,
        mensaje=a.mensaje,
        creada_en=a.creada_en.isoformat(),
    )


def serializar_explicacion(e: Explicacion) -> ExplicacionResponse:
    """Serializa una entidad ``Explicacion`` al modelo de respuesta de generación."""
    return ExplicacionResponse(
        id=str(e.id),
        recomendacion_id=str(e.recomendacion_id),
        resumen=e.resumen,
        detalle=e.detalle,
        evidencias=_evidencias(e),
        fecha_generacion=e.fecha_generacion.isoformat(),
    )


def serializar_consulta_explicacion(e: Explicacion) -> ConsultarExplicacionResponse:
    """Serializa una entidad ``Explicacion`` al modelo de respuesta de consulta."""
    return ConsultarExplicacionResponse(
        id=str(e.id),
        recomendacion_id=str(e.recomendacion_id),
        resumen=e.resumen,
        detalle=e.detalle,
        evidencias=_evidencias(e),
        fecha_generacion=e.fecha_generacion.isoformat(),
    )
