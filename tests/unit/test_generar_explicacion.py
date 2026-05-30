from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.use_cases.generar_explicacion import (
    GenerarExplicacionCommand,
    GenerarExplicacionUseCase,
)
from src.domain.services.motor_explicabilidad import MotorExplicabilidad


@pytest.fixture
def use_case():
    repo = AsyncMock()
    repo.save.side_effect = lambda e: e
    cache = AsyncMock()
    events = MagicMock()
    return GenerarExplicacionUseCase(
        repo, cache, events, MotorExplicabilidad(), cache_ttl=60
    )


async def test_guarda_cachea_y_publica_evento(use_case):
    cmd = GenerarExplicacionCommand(
        recomendacion_id=uuid4(),
        pesos_atencion=[
            {
                "interaccion_referencia_id": uuid4(),
                "peso": 0.8,
                "concepto": "álgebra",
            }
        ],
    )
    explicacion = await use_case.execute(cmd)

    assert explicacion.resumen
    use_case._repo.save.assert_awaited_once()
    use_case._cache.set_explicacion.assert_awaited_once()
    use_case._event_publisher.publish.assert_called_once()
