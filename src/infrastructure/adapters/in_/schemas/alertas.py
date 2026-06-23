"""Contratos HTTP de las alertas de riesgo académico (lectura del docente)."""

from pydantic import BaseModel


class AlertaResponse(BaseModel):
    """Alerta de riesgo académico para el dashboard docente."""

    id: str
    estudiante_id: str
    curso_id: str
    nivel_riesgo: str
    mensaje: str
    creada_en: str
