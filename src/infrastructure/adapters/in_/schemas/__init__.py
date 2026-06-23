"""Contratos Pydantic (Request/Response) del adaptador de entrada HTTP.

Organizados por concern (alertas, explicaciones) en vez de un único archivo,
según buenas prácticas de organización. Se re-exportan aquí para que las rutas
importen desde `...adapters.in_.schemas` sin conocer el submódulo.
"""

from .alertas import AlertaResponse
from .explicaciones import (
    ConsultarExplicacionResponse,
    EvidenciaResponse,
    ExplainRequest,
    ExplicacionResponse,
    PesoAtencionRequest,
)

__all__ = [
    "AlertaResponse",
    "PesoAtencionRequest",
    "ExplainRequest",
    "EvidenciaResponse",
    "ExplicacionResponse",
    "ConsultarExplicacionResponse",
]
