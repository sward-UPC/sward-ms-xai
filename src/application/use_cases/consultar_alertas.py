from uuid import UUID

from src.domain.entities.alerta_academica import AlertaAcademica
from src.application.ports.out_.xai_repository_port import XaiRepositoryPort


class ConsultarAlertasUseCase:
    """Lista las alertas de riesgo de un curso para el dashboard docente."""

    def __init__(self, repo: XaiRepositoryPort):
        self._repo = repo

    async def execute(self, curso_id: UUID) -> list[AlertaAcademica]:
        return await self._repo.find_alertas_por_curso(curso_id)
