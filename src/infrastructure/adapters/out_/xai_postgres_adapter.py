import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.alerta_academica import AlertaAcademica
from src.domain.entities.explicacion import (
    EvidenciaExplicativa,
    Explicacion,
    PesoAtencion,
)
from src.application.ports.out_.xai_repository_port import XaiRepositoryPort
from src.infrastructure.db.models.xai_models import AlertModel, ExplanationModel


class XaiPostgresAdapter(XaiRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def save(self, e: Explicacion) -> Explicacion:
        evidencias_json = json.dumps(
            [
                {"tipo": ev.tipo, "descripcion": ev.descripcion, "impacto": ev.impacto}
                for ev in e.evidencias
            ]
        )
        pesos_json = json.dumps(
            [
                {
                    "interaccion_referencia_id": str(p.interaccion_referencia_id),
                    "peso": p.peso,
                    "concepto": p.concepto,
                }
                for p in e.pesos
            ]
        )
        m = ExplanationModel(
            id=e.id,
            recomendacion_id=e.recomendacion_id,
            resumen=e.resumen,
            detalle=e.detalle,
            evidencias_json=evidencias_json,
            pesos_json=pesos_json,
            fecha_generacion=e.fecha_generacion,
        )
        self._s.add(m)
        await self._s.flush()
        return e

    async def find_by_recomendacion(self, recomendacion_id: UUID) -> Explicacion | None:
        res = await self._s.execute(
            select(ExplanationModel)
            .where(ExplanationModel.recomendacion_id == recomendacion_id)
            .order_by(ExplanationModel.fecha_generacion.desc())
            .limit(1)
        )
        m = res.scalar_one_or_none()
        return _to_entity(m) if m else None

    async def find_alertas_por_curso(self, curso_id: UUID) -> list[AlertaAcademica]:
        res = await self._s.execute(
            select(AlertModel)
            .where(AlertModel.curso_id == curso_id)
            .order_by(AlertModel.creada_en.desc())
        )
        return [
            AlertaAcademica(
                id=m.id,
                estudiante_id=m.estudiante_id,
                curso_id=m.curso_id,
                nivel_riesgo=m.nivel_riesgo,
                mensaje=m.mensaje,
                creada_en=m.creada_en,
            )
            for m in res.scalars().all()
        ]


def _to_entity(m: ExplanationModel) -> Explicacion:
    evidencias = [
        EvidenciaExplicativa(**ev) for ev in json.loads(m.evidencias_json or "[]")
    ]
    pesos = [
        PesoAtencion(
            interaccion_referencia_id=UUID(p["interaccion_referencia_id"]),
            peso=p["peso"],
            concepto=p["concepto"],
        )
        for p in json.loads(m.pesos_json or "[]")
    ]
    return Explicacion(
        id=m.id,
        recomendacion_id=m.recomendacion_id,
        resumen=m.resumen,
        detalle=m.detalle,
        evidencias=evidencias,
        pesos=pesos,
        fecha_generacion=m.fecha_generacion,
    )
