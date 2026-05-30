from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.consultar_explicacion import (
    ConsultarExplicacionCommand,
    ConsultarExplicacionUseCase,
)
from src.domain.entities.explicacion import Explicacion


@pytest.fixture
def recomendacion_id():
    return uuid4()


def _cache_payload(recomendacion_id):
    return {
        "id": str(uuid4()),
        "recomendacion_id": str(recomendacion_id),
        "resumen": "desde cache",
        "detalle": "detalle cache",
        "evidencias": [],
        "fecha_generacion": datetime.now(timezone.utc).isoformat(),
    }


async def test_devuelve_desde_cache_sin_tocar_repo(recomendacion_id):
    repo = AsyncMock()
    cache = AsyncMock()
    cache.get_explicacion.return_value = _cache_payload(recomendacion_id)
    uc = ConsultarExplicacionUseCase(repo, cache, cache_ttl=60)

    explicacion = await uc.execute(
        ConsultarExplicacionCommand(recomendacion_id=recomendacion_id)
    )

    assert explicacion.resumen == "desde cache"
    repo.find_by_recomendacion.assert_not_awaited()
    cache.set_explicacion.assert_not_awaited()


async def test_cae_al_repo_si_no_hay_cache(recomendacion_id):
    repo = AsyncMock()
    repo.find_by_recomendacion.return_value = Explicacion(
        recomendacion_id=recomendacion_id, resumen="desde repo"
    )
    cache = AsyncMock()
    cache.get_explicacion.return_value = None
    uc = ConsultarExplicacionUseCase(repo, cache, cache_ttl=60)

    explicacion = await uc.execute(
        ConsultarExplicacionCommand(recomendacion_id=recomendacion_id)
    )

    assert explicacion.resumen == "desde repo"
    repo.find_by_recomendacion.assert_awaited_once()
    cache.set_explicacion.assert_awaited_once()
