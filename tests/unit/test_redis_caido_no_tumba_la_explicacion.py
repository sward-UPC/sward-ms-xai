"""Que se caiga la caché no puede costar una explicación.

El 5 de octubre de 2026 una petición a POST /xai/explain respondió 500. La
explicación ya estaba generada y guardada en la base; lo que falló fue el
último paso, meterla en la caché de Redis. La excepción subió sin capturar, la
sesión se revirtió y el estudiante se quedó sin su explicación.

Es la segunda vez que la explicabilidad —que es la contribución de la tesis— se
pierde por un servicio de apoyo. La primera fue el 1 de octubre, cuando a
ms-xai le faltaba el permiso para publicar en EventBridge.

Aquí Redis es caché pura: si no se puede leer, se regenera; si no se puede
escribir, no se guarda y ya.
"""

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from src.infrastructure.adapters.out_ import redis_adapter as modulo
from src.infrastructure.adapters.out_.redis_adapter import RedisAdapter

RECOMENDACION = "22222222-2222-2222-2222-222222222222"


class _RedisCaido:
    def __getattr__(self, nombre):
        async def falla(*args, **kwargs):
            raise RedisConnectionError("Error UNKNOWN while writing to socket.")

        return falla


@pytest.fixture
def adaptador(monkeypatch):
    monkeypatch.setattr(modulo.redis, "from_url", lambda *a, **k: _RedisCaido())
    return RedisAdapter("redis://no-existe:6379/0")


async def test_leer_la_cache_caida_es_un_fallo_de_cache(adaptador):
    # Devolver None significa «no está en caché»: se regenera la explicación.
    assert await adaptador.get_explicacion(RECOMENDACION) is None


async def test_guardar_en_la_cache_caida_no_tumba_la_explicacion(adaptador):
    # Este fue el 500 del 5 de octubre: la explicación ya existía y se perdió.
    await adaptador.set_explicacion(RECOMENDACION, {"resumen": "algo"}, 300)
