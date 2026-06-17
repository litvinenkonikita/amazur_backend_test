from decimal import Decimal

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.common import Base, CampaignStatus, TimestampMixin, UUIDPrimaryKeyMixin, decimal_column, status_enum


class Campaign(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_status = mapped_column(status_enum, nullable=False, default=CampaignStatus.ACTIVE)
    target_status = mapped_column(status_enum, nullable=False, default=CampaignStatus.ACTIVE)
    is_managed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    budget_limit: Mapped[Decimal | None] = decimal_column(nullable=True)
    spend_today: Mapped[Decimal] = mapped_column(nullable=False, default=Decimal("0.00"))
    stock_days_left: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock_days_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    schedules = relationship(
        "CampaignSchedule",
        back_populates="campaign",
        cascade="all, delete-orphan",
        order_by="CampaignSchedule.day_of_week, CampaignSchedule.start_time",
    )
    evaluation_logs = relationship(
        "RuleEvaluationLog",
        back_populates="campaign",
        cascade="all, delete-orphan",
        order_by="desc(RuleEvaluationLog.created_at)",
    )
