from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.use_cases.consultar_alertas import ConsultarAlertasUseCase
from src.application.use_cases.consultar_explicacion import (
    ConsultarExplicacionCommand,
    ConsultarExplicacionUseCase,
)
from src.application.use_cases.generar_explicacion import (
    GenerarExplicacionCommand,
    GenerarExplicacionUseCase,
)
from src.infrastructure.adapters.in_.mappers import (
    serializar_alerta,
    serializar_consulta_explicacion,
    serializar_explicacion,
)
from src.infrastructure.adapters.in_.schemas import (
    AlertaResponse,
    ConsultarExplicacionResponse,
    ExplainRequest,
    ExplicacionResponse,
)
from src.infrastructure.dependencies import (
    get_consultar_alertas_uc,
    get_consultar_explicacion_uc,
    get_generar_explicacion_uc,
    require_jwt,
    require_service_key,
)

router = APIRouter(prefix="/xai", tags=["XAI"])


@router.get("/alerts", summary="Alertas de riesgo del curso (docente)")
async def listar_alertas(
    courseId: UUID,  # noqa: N803 (contrato camelCase con el frontend)
    _user: dict = Depends(require_jwt),
    uc: ConsultarAlertasUseCase = Depends(get_consultar_alertas_uc),
) -> list[AlertaResponse]:
    """Lista las alertas de riesgo académico de un curso, más recientes primero.

    Las genera `sward-lambda-alertas`; aquí solo se leen para el docente.

    **Auth:** JWT
    """
    alertas = await uc.execute(courseId)
    return [serializar_alerta(a) for a in alertas]


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
    _: None = Depends(require_service_key),
    uc: GenerarExplicacionUseCase = Depends(get_generar_explicacion_uc),
) -> ExplicacionResponse:
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
    explicacion = await uc.execute(
        GenerarExplicacionCommand(
            recomendacion_id=body.recomendacion_id,
            pesos_atencion=[p.model_dump() for p in body.pesos_atencion],
        )
    )
    return serializar_explicacion(explicacion)


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
    _: None = Depends(require_service_key),
    uc: ConsultarExplicacionUseCase = Depends(get_consultar_explicacion_uc),
) -> ConsultarExplicacionResponse:
    """
    Obtiene la explicación generada previamente de una recomendación.

    **Flujo:**
    1. Busca la explicación en cache/base de datos
    2. Retorna explicación completa si existe

    **SLA:** ≤500ms

    **Autenticación:** Bearer JWT (requerido)
    """
    explicacion = await uc.execute(
        ConsultarExplicacionCommand(recomendacion_id=recomendacion_id)
    )
    return serializar_consulta_explicacion(explicacion)
