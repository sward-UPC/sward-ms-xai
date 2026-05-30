from src.domain.entities.explicacion import EvidenciaExplicativa, PesoAtencion


class MotorExplicabilidad:
    """Convierte los pesos de atención del modelo SAKT en lenguaje natural.

    En modo desarrollo funciona con lógica simple (sin LLM): ordena los pesos
    de mayor a menor influencia y construye una explicación legible para el
    estudiante.
    """

    def generar_texto(self, pesos: list[PesoAtencion]) -> str:
        if not pesos:
            return "No hay suficiente información para explicar esta recomendación."
        ordenados = sorted(pesos, key=lambda p: p.peso, reverse=True)
        principal = ordenados[0]
        texto = (
            "Esta recomendación se basa principalmente en tu desempeño en "
            f"{principal.concepto} (influencia {principal.peso:.0%})"
        )
        secundarios = ordenados[1:3]
        if secundarios:
            extra = ", ".join(f"{p.concepto} ({p.peso:.0%})" for p in secundarios)
            texto += f". También influyen: {extra}"
        return texto + "."

    def generar_evidencias(
        self, pesos: list[PesoAtencion]
    ) -> list[EvidenciaExplicativa]:
        ordenados = sorted(pesos, key=lambda p: p.peso, reverse=True)
        return [
            EvidenciaExplicativa(
                tipo="peso_atencion",
                descripcion=f"Concepto '{p.concepto}' con influencia {p.peso:.0%}",
                impacto=p.peso,
            )
            for p in ordenados
        ]
