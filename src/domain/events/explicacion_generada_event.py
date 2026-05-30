from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sward_shared.events.domain_event import DomainEvent


@dataclass
class ExplicacionGeneradaEvent(DomainEvent):
    explicacion_id: UUID = field(default_factory=uuid4)
    recomendacion_id: UUID = field(default_factory=uuid4)
    source: str = "sward-ms-xai"

    @property
    def event_type(self) -> str:
        return "sward.xai.ExplicacionGenerada"
