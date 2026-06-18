"""Test del endpoint GET /xai/alerts (lectura docente)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.application.use_cases.consultar_alertas import ConsultarAlertasUseCase
from src.domain.entities.alerta_academica import AlertaAcademica
from src.infrastructure.adapters.in_.main import app
from src.infrastructure.dependencies import get_consultar_alertas_uc, require_jwt

CURSO = uuid4()


class _FakeRepo:
    async def find_alertas_por_curso(self, curso_id):
        return [
            AlertaAcademica(
                estudiante_id=uuid4(),
                curso_id=curso_id,
                nivel_riesgo="critico",
                mensaje="Riesgo crítico, requiere intervención.",
                creada_en=datetime(2026, 6, 18, tzinfo=timezone.utc),
            )
        ]


@pytest.mark.asyncio
async def test_listar_alertas_devuelve_alertas():
    app.dependency_overrides[require_jwt] = lambda: {
        "sub": str(uuid4()),
        "rol": "docente",
    }
    app.dependency_overrides[get_consultar_alertas_uc] = lambda: (
        ConsultarAlertasUseCase(_FakeRepo())
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/xai/alerts?courseId={CURSO}")
    app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["nivel_riesgo"] == "critico"
    assert data[0]["mensaje"]


@pytest.mark.asyncio
async def test_listar_alertas_sin_jwt_es_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/xai/alerts?courseId={CURSO}")
    assert resp.status_code in (401, 403)
