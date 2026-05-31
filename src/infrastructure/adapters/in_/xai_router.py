from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.application.use_cases.consultar_explicacion import (
    ConsultarExplicacionCommand,
    ConsultarExplicacionUseCase,
)
from src.application.use_cases.generar_explicacion import (
    GenerarExplicacionCommand,
    GenerarExplicacionUseCase,
)
from src.domain.entities.explicacion import Explicacion
from src.infrastructure.dependencies import (
    get_consultar_explicacion_uc,
    get_generar_explicacion_uc,
)

router = APIRouter(prefix="/xai", tags=["XAI"])


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


def _serialize(e: Explicacion) -> ExplicacionResponse:
    """Serializa una entidad Explicacion a modelo de respuesta API."""
    return ExplicacionResponse(
        id=str(e.id),
        recomendacion_id=str(e.recomendacion_id),
        resumen=e.resumen,
        detalle=e.detalle,
        evidencias=[
            EvidenciaResponse(
                tipo=ev.tipo,
                descripcion=ev.descripcion,
                impacto=ev.impacto,
            )
            for ev in e.evidencias
        ],
        fecha_generacion=e.fecha_generacion.isoformat(),
    )


@router.post(
    "/explain",
    status_code=status.HTTP_201_CREATED,
    response_model=ExplicacionResponse,
    responses={
        201: {"description": "Explicación generada exitosamente"},
        400: {
            "description": "Datos de entrada inválidos o recomendación no encontrada"
        },
        401: {"description": "No autorizado - requiere autenticación JWT"},
        500: {"description": "Error interno en modelo XAI"},
    },
)
async def explain(
    body: ExplainRequest,
    uc: GenerarExplicacionUseCase = Depends(get_generar_explicacion_uc),
):
    """
    Genera explicación interoperable (XAI) para una recomendación.

    **Flujo:**
    1. Valida que la recomendación existe
    2. Calcula importancia de factores (SHAP-like) basado en pesos
    3. Genera explicación natural y evidencias cuantificadas
    4. Retorna respuesta estructurada con resumen y detalle

    **SLA:** ≤3 segundos

    **Autenticación:** Bearer JWT (requerido)
    """
    try:
        explicacion = await uc.execute(
            GenerarExplicacionCommand(
                recomendacion_id=body.recomendacion_id,
                pesos_atencion=[p.model_dump() for p in body.pesos_atencion],
            )
        )
        return _serialize(explicacion)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/explain/{recomendacion_id}",
    response_model=ConsultarExplicacionResponse,
    responses={
        200: {"description": "Explicación obtenida exitosamente"},
        401: {"description": "No autorizado - requiere autenticación JWT"},
        404: {"description": "Explicación no encontrada para la recomendación"},
        500: {"description": "Error interno del servidor"},
    },
)
async def get_explanation(
    recomendacion_id: UUID,
    uc: ConsultarExplicacionUseCase = Depends(get_consultar_explicacion_uc),
):
    """
    Obtiene la explicación generada previamente de una recomendación.

    **Flujo:**
    1. Busca la explicación en cache/base de datos
    2. Retorna explicación completa si existe

    **SLA:** ≤500ms

    **Autenticación:** Bearer JWT (requerido)
    """
    try:
        explicacion = await uc.execute(
            ConsultarExplicacionCommand(recomendacion_id=recomendacion_id)
        )
        if explicacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Explicación no encontrada",
            )
        return ConsultarExplicacionResponse(
            id=str(explicacion.id),
            recomendacion_id=str(explicacion.recomendacion_id),
            resumen=explicacion.resumen,
            detalle=explicacion.detalle,
            evidencias=[
                EvidenciaResponse(
                    tipo=ev.tipo,
                    descripcion=ev.descripcion,
                    impacto=ev.impacto,
                )
                for ev in explicacion.evidencias
            ],
            fecha_generacion=explicacion.fecha_generacion.isoformat(),
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
