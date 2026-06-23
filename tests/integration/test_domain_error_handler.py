"""El handler central traduce errores de dominio a HTTP (sin try/except inline)."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.application.use_cases.consultar_explicacion import ConsultarExplicacionUseCase
from src.infrastructure.adapters.in_.main import app
from src.infrastructure.dependencies import (
    get_consultar_explicacion_uc,
    require_service_key,
)


class _RepoVacio:
    async def find_by_recomendacion(self, recomendacion_id):
        return None


class _CacheVacia:
    async def get_explicacion(self, recomendacion_id):
        return None

    async def set_explicacion(self, recomendacion_id, data, ttl):
        return None


@pytest.mark.asyncio
async def test_explicacion_inexistente_devuelve_404():
    app.dependency_overrides[require_service_key] = lambda: None
    app.dependency_overrides[get_consultar_explicacion_uc] = lambda: (
        ConsultarExplicacionUseCase(_RepoVacio(), _CacheVacia(), cache_ttl=60)
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/xai/explain/{uuid4()}")
    app.dependency_overrides.clear()

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Explicación no encontrada"
