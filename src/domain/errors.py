"""Jerarquía de errores de dominio del microservicio XAI.

El núcleo (dominio/aplicación) lanza estas excepciones para señalar la
violación de una regla de negocio o un recurso ausente. Los adaptadores de
entrada NO deben capturarlas de forma dispersa: un único *exception handler*
en el borde HTTP las traduce al código de estado correspondiente.
"""


class DomainError(Exception):
    """Error base de dominio. Toda excepción de negocio hereda de aquí."""


class ValidationError(DomainError):
    """Una invariante de dominio fue violada (datos de entrada inválidos)."""


class NotFoundError(DomainError):
    """No existe el recurso de dominio solicitado."""
