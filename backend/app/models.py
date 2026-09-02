import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Valuation(Base):
    __tablename__ = "valuations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    target_name: Mapped[str] = mapped_column(String(255))
    acquirer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    offer_price: Mapped[float] = mapped_column(Float)
    current_share_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    consideration_type: Mapped[str] = mapped_column(String(50), default="cash")

    inputs: Mapped[dict] = mapped_column(JSONB)
    results: Mapped[dict] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    opinions: Mapped[list["FairnessOpinion"]] = relationship(back_populates="valuation", cascade="all, delete-orphan")


class FairnessOpinion(Base):
    __tablename__ = "fairness_opinions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    valuation_id: Mapped[str] = mapped_column(ForeignKey("valuations.id"))

    narrative: Mapped[str] = mapped_column(Text)
    model_used: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    valuation: Mapped["Valuation"] = relationship(back_populates="opinions")
