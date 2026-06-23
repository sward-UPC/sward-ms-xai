"""Contratos HTTP de la generación y consulta de explicaciones (XAI)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PesoAtencionRequest(BaseModel):
    """Especifica el peso de una interacción en el análisis de explicabilidad."""

    model_config = ConfigDict(extra="forbid")

    interaccion_referencia_id: UUID = Field(
        ...,
        description="UUID de la interacción educativa de referencia",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440003"},
    )
    peso: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Peso normalizado de la interacción [0, 1]",
        json_schema_extra={"example": 0.85},
    )
    concepto: str = Field(
        ...,
        max_length=255,
        description="Concepto educativo asociado a la interacción",
        json_schema_extra={"example": "Búsqueda binaria"},
    )


class ExplainRequest(BaseModel):
    """Solicitud para generar explicación de una recomendación."""

    model_config = ConfigDict(extra="forbid")

    recomendacion_id: UUID = Field(
        ...,
        description="UUID de la recomendación a explicar",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440002"},
    )
    pesos_atencion: list[PesoAtencionRequest] = Field(
        ...,
        max_length=512,
        description="Pesos de atención para factores de influencia",
        min_length=1,
    )


class EvidenciaResponse(BaseModel):
    """Evidencia que respalda la explicación de la recomendación."""

    model_config = ConfigDict(extra="forbid")

    tipo: str = Field(
        ...,
        description="Tipo de evidencia",
        json_schema_extra={
            "enum": ["concepto_dominado", "deficit", "alineacion"],
            "example": "concepto_dominado",
        },
    )
    descripcion: str = Field(
        ...,
        description="Descripción detallada de la evidencia",
        json_schema_extra={"example": "El estudiante domina Algoritmos (0.92 mastery)"},
    )
    impacto: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Peso de esta evidencia en la decisión final",
        json_schema_extra={"example": 0.65},
    )


class ExplicacionResponse(BaseModel):
    """Explicación generada para una recomendación."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        description="UUID de la explicación",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440004"},
    )
    recomendacion_id: str = Field(
        ...,
        description="UUID de la recomendación explicada",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440002"},
    )
    resumen: str = Field(
        ...,
        description="Resumen ejecutivo de la explicación (max 200 caracteres)",
        json_schema_extra={
            "example": "Recomendado por dominio en Búsqueda y deficiencia en Ordenamiento"
        },
    )
    detalle: str = Field(
        ...,
        description="Análisis detallado con factores de influencia",
        json_schema_extra={
            "example": "Basado en análisis SAKT de interacciones: Algoritmos 0.92, Estructuras 0.78..."
        },
    )
    evidencias: list[EvidenciaResponse] = Field(
        ...,
        description="Lista de evidencias que respaldan la recomendación",
    )
    fecha_generacion: str = Field(
        ...,
        description="Timestamp ISO 8601 de generación",
        json_schema_extra={"example": "2025-05-31T14:30:00Z"},
    )


class ConsultarExplicacionResponse(BaseModel):
    """Respuesta al consultar una explicación existente."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        description="UUID de la explicación",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440004"},
    )
    recomendacion_id: str = Field(
        ...,
        description="UUID de la recomendación explicada",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440002"},
    )
    resumen: str = Field(
        ...,
        description="Resumen ejecutivo",
        json_schema_extra={
            "example": "Recomendado por dominio en Búsqueda y deficiencia en Ordenamiento"
        },
    )
    detalle: str = Field(
        ...,
        description="Análisis detallado",
    )
    evidencias: list[EvidenciaResponse] = Field(
        ...,
        description="Evidencias respaldarorias",
    )
    fecha_generacion: str = Field(
        ...,
        description="Timestamp ISO 8601 de generación",
        json_schema_extra={"example": "2025-05-31T14:30:00Z"},
    )
