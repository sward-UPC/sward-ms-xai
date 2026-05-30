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
    assert "principalmente en tu desempeño en álgebra" in texto
    assert evidencias[0].impacto == 0.9
    assert evidencias[0].descripcion.startswith("Concepto 'álgebra'")
