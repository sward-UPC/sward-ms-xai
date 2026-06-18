from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AlertModel(Base):
    """Alerta de riesgo académico. La escribe sward-lambda-alertas; la lee el
    dashboard docente. El esquema coincide con el INSERT de la lambda."""

    __tablename__ = "academic_alerts"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    estudiante_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    curso_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    nivel_riesgo: Mapped[str] = mapped_column(String(20), default="alto")
    mensaje: Mapped[str] = mapped_column(Text, default="")
    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class ExplanationModel(Base):
    __tablename__ = "explanations"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    recomendacion_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    resumen: Mapped[str] = mapped_column(Text, default="")
    detalle: Mapped[str] = mapped_column(Text, default="")
    evidencias_json: Mapped[str] = mapped_column(Text, default="[]")
    pesos_json: Mapped[str] = mapped_column(Text, default="[]")
    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
