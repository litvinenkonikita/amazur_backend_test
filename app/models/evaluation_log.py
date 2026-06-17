import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.common import Base, UUIDPrimaryKeyMixin, jsonb_type, status_enum


class RuleEvaluationLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "rule_evaluation_logs"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    triggered_rule: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_target = mapped_column(status_enum, nullable=False)
    new_target = mapped_column(status_enum, nullable=False)
    context: Mapped[dict] = mapped_column(jsonb_type, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())

    campaign = relationship("Campaign", back_populates="evaluation_logs")
