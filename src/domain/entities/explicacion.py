from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class PesoAtencion:
    interaccion_referencia_id: UUID = field(default_factory=uuid4)
    peso: float = 0.0
    concepto: str = ""


@dataclass
class EvidenciaExplicativa:
    tipo: str = ""
    descripcion: str = ""
    impacto: float = 0.0


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
