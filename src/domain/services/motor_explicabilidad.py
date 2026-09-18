from src.domain.entities.explicacion import EvidenciaExplicativa, PesoAtencion


class MotorExplicabilidad:
    """Convierte los pesos de atención del modelo SAKT en lenguaje natural.

    Ordena los pesos de mayor a menor y describe dónde se fijó el modelo. No usa
    «se basa», «influye» ni «influencia»: la atención de SAKT, medida con ERASER
    en la tesis, resultó suficiente pero no necesaria. Lo más atendido basta para
    llegar a la predicción, pero no es su causa, y un texto causal afirmaría más
    de lo que se comprobó. Por eso el peso se nombra como lo que es: una parte de
    la atención.
    """

    def generar_texto(self, pesos: list[PesoAtencion]) -> str:
        if not pesos:
            return "No hay suficiente información para explicar esta recomendación."
        ordenados = sorted(pesos, key=lambda p: p.peso, reverse=True)
        principal = ordenados[0]
        texto = (
            "Al estimar tu siguiente paso, el modelo prestó más atención a tu "
            f"interacción en {principal.concepto} ({principal.peso:.0%} de la atención)"
        )
        # Varias interacciones pueden ser del mismo concepto: se nombra cada
        # concepto una sola vez, con su interacción más atendida.
        vistos = {principal.concepto}
        secundarios = []
        for p in ordenados[1:]:
            if p.concepto not in vistos:
                vistos.add(p.concepto)
                secundarios.append(p)
            if len(secundarios) == 2:
                break
        if secundarios:
            extra = ", ".join(f"{p.concepto} ({p.peso:.0%})" for p in secundarios)
            texto += f". Le siguen: {extra}"
        return (
            texto + ". La atención muestra dónde se fijó el modelo, no la causa de "
            "la recomendación."
        )

    def generar_evidencias(
        self, pesos: list[PesoAtencion]
    ) -> list[EvidenciaExplicativa]:
        ordenados = sorted(pesos, key=lambda p: p.peso, reverse=True)
        return [
            EvidenciaExplicativa(
                tipo="peso_atencion",
                descripcion=f"Concepto '{p.concepto}' con {p.peso:.0%} de la atención",
                impacto=p.peso,
            )
            for p in ordenados
        ]
