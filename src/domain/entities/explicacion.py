from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.errors import ValidationError


@dataclass
class PesoAtencion:
    interaccion_referencia_id: UUID = field(default_factory=uuid4)
    peso: float = 0.0
    concepto: str = ""

    def __post_init__(self) -> None:
        # Invariante de dominio: el peso de atención está normalizado en [0, 1].
        if not 0.0 <= self.peso <= 1.0:
            raise ValidationError(
                f"El peso de atención debe estar en [0, 1]; recibido: {self.peso}"
            )


@dataclass
class EvidenciaExplicativa:
    tipo: str = ""
    descripcion: str = ""
    impacto: float = 0.0

    def __post_init__(self) -> None:
        # Invariante de dominio: el impacto de la evidencia está en [0, 1].
        if not 0.0 <= self.impacto <= 1.0:
            raise ValidationError(
                f"El impacto de la evidencia debe estar en [0, 1]; "
                f"recibido: {self.impacto}"
            )


@dataclass
class Explicacion:
    id: UUID = field(default_factory=uuid4)
    recomendacion_id: UUID = field(default_factory=uuid4)
    resumen: str = ""
    detalle: str = ""
    evidencias: list[EvidenciaExplicativa] = field(default_factory=list)
    pesos: list[PesoAtencion] = field(default_factory=list)
    fecha_generacion: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
