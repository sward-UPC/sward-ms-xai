from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class AlertaAcademica:
    """Alerta de riesgo académico para el docente (generada por lambda-alertas)."""

    estudiante_id: UUID
    curso_id: UUID
    nivel_riesgo: str
    mensaje: str
    id: UUID = field(default_factory=uuid4)
    creada_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
