from uuid import uuid4

from src.domain.entities.explicacion import PesoAtencion
from src.domain.services.motor_explicabilidad import MotorExplicabilidad


def test_genera_texto_no_vacio():
    motor = MotorExplicabilidad()
    pesos = [
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.7, concepto="álgebra"),
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.3, concepto="lectura"),
    ]
    texto = motor.generar_texto(pesos)
    assert texto
    assert "álgebra" in texto


def test_prioriza_peso_mas_alto():
    motor = MotorExplicabilidad()
    pesos = [
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.2, concepto="lectura"),
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.9, concepto="álgebra"),
    ]
    texto = motor.generar_texto(pesos)
    evidencias = motor.generar_evidencias(pesos)
    assert "más atención a tu interacción en álgebra" in texto
    assert evidencias[0].impacto == 0.9
    assert evidencias[0].descripcion.startswith("Concepto 'álgebra'")


def test_no_afirma_causalidad():
    # La atención es suficiente pero no necesaria: el texto describe dónde se
    # fijó el modelo y nunca que eso sea la causa de la recomendación.
    motor = MotorExplicabilidad()
    pesos = [
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.5, concepto="grafos"),
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.3, concepto="árboles"),
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.2, concepto="pilas"),
    ]
    textos = [motor.generar_texto(pesos)] + [
        e.descripcion for e in motor.generar_evidencias(pesos)
    ]
    for t in textos:
        bajo = t.lower()
        for causal in ("se basa", "influy", "influencia", "debido a", "porque"):
            assert causal not in bajo, f"lenguaje causal «{causal}» en: {t}"
    assert "no la causa" in textos[0]


def test_cada_concepto_se_nombra_una_vez():
    motor = MotorExplicabilidad()
    pesos = [
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.4, concepto="grafos"),
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.35, concepto="grafos"),
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=0.25, concepto="pilas"),
    ]
    texto = motor.generar_texto(pesos)
    assert texto.count("grafos") == 1
    assert "Le siguen: pilas (25%)" in texto
