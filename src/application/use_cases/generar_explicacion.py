from dataclasses import dataclass, field
from uuid import UUID

from src.domain.entities.explicacion import Explicacion, PesoAtencion
from src.domain.events.explicacion_generada_event import ExplicacionGeneradaEvent
from src.domain.ports.out_.cache_port import CachePort
from src.domain.ports.out_.event_publisher_port import EventPublisherPort
from src.domain.ports.out_.xai_repository_port import XaiRepositoryPort
from src.domain.services.motor_explicabilidad import MotorExplicabilidad


@dataclass
class GenerarExplicacionCommand:
    recomendacion_id: UUID
    pesos_atencion: list[dict] = field(default_factory=list)


class GenerarExplicacionUseCase:
    """RF-004-05: genera una explicación con latencia objetivo < 500ms.

    En dev el motor no usa LLM, por lo que no hay operaciones pesadas.
    """

    def __init__(
        self,
        repo: XaiRepositoryPort,
        cache: CachePort,
        event_publisher: EventPublisherPort,
        motor: MotorExplicabilidad,
        cache_ttl: int = 3600,
    ):
        self._repo = repo
        self._cache = cache
        self._event_publisher = event_publisher
        self._motor = motor
        self._cache_ttl = cache_ttl

    async def execute(self, cmd: GenerarExplicacionCommand) -> Explicacion:
        pesos = [
            PesoAtencion(
                interaccion_referencia_id=p["interaccion_referencia_id"],
                peso=p["peso"],
                concepto=p["concepto"],
            )
            for p in cmd.pesos_atencion
        ]
        resumen = self._motor.generar_texto(pesos)
        evidencias = self._motor.generar_evidencias(pesos)
        detalle = " ".join(e.descripcion for e in evidencias)

        explicacion = Explicacion(
            recomendacion_id=cmd.recomendacion_id,
            resumen=resumen,
            detalle=detalle,
            evidencias=evidencias,
            pesos=pesos,
        )
        guardada = await self._repo.save(explicacion)
        await self._cache.set_explicacion(
            cmd.recomendacion_id, _to_dict(guardada), self._cache_ttl
        )
        self._event_publisher.publish(
            ExplicacionGeneradaEvent(
                explicacion_id=guardada.id,
                recomendacion_id=guardada.recomendacion_id,
            )
        )
        return guardada


def _to_dict(e: Explicacion) -> dict:
    return {
        "id": str(e.id),
        "recomendacion_id": str(e.recomendacion_id),
        "resumen": e.resumen,
        "detalle": e.detalle,
        "evidencias": [
            {"tipo": ev.tipo, "descripcion": ev.descripcion, "impacto": ev.impacto}
            for ev in e.evidencias
        ],
        "fecha_generacion": e.fecha_generacion.isoformat(),
    }
