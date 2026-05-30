"""Fixtures de integración para el microservicio XAI (in-process).

La app se ejerce con httpx.AsyncClient + ASGITransport (sin levantar servidor).
Para la documentación de API (/scalar, /openapi.json) no se requieren overrides
de puertos ni autenticación, por lo que se expone un cliente anónimo simple.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.infrastructure.adapters.in_.main import app


@pytest_asyncio.fixture
async def anon_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
