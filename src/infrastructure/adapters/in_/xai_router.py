from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
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
    model_config = ConfigDict(extra="forbid")

    interaccion_referencia_id: UUID
    peso: float = Field(ge=0.0, le=1.0)
    concepto: str = Field(max_length=255)


class ExplainRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recomendacion_id: UUID
    pesos_atencion: list[PesoAtencionRequest] = Field(max_length=512)


def _serialize(e: Explicacion) -> dict:
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


@router.post("/explain", status_code=201)
async def explain(
    body: ExplainRequest,
    uc: GenerarExplicacionUseCase = Depends(get_generar_explicacion_uc),
):
    explicacion = await uc.execute(
        GenerarExplicacionCommand(
            recomendacion_id=body.recomendacion_id,
            pesos_atencion=[p.model_dump() for p in body.pesos_atencion],
        )
    )
    return _serialize(explicacion)


@router.get("/explain/{recomendacion_id}")
async def get_explanation(
    recomendacion_id: UUID,
    uc: ConsultarExplicacionUseCase = Depends(get_consultar_explicacion_uc),
):
    explicacion = await uc.execute(
        ConsultarExplicacionCommand(recomendacion_id=recomendacion_id)
    )
    if explicacion is None:
        raise HTTPException(status_code=404, detail="Explicación no encontrada")
    return _serialize(explicacion)
