"""Invariantes de dominio: el peso/impacto normalizado vive en el VO."""

from uuid import uuid4

import pytest

from src.domain.entities.explicacion import EvidenciaExplicativa, PesoAtencion
from src.domain.errors import ValidationError


@pytest.mark.parametrize("peso", [-0.1, 1.1, 2.0])
def test_peso_atencion_fuera_de_rango_falla(peso):
    with pytest.raises(ValidationError):
        PesoAtencion(interaccion_referencia_id=uuid4(), peso=peso, concepto="x")


@pytest.mark.parametrize("peso", [0.0, 0.5, 1.0])
def test_peso_atencion_en_rango_ok(peso):
    vo = PesoAtencion(interaccion_referencia_id=uuid4(), peso=peso, concepto="x")
    assert vo.peso == peso


def test_evidencia_impacto_fuera_de_rango_falla():
    with pytest.raises(ValidationError):
        EvidenciaExplicativa(tipo="t", descripcion="d", impacto=1.5)
