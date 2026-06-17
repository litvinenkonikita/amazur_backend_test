import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CampaignStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"


class RuleName(StrEnum):
    MANAGEMENT_DISABLED = "management_disabled"
    SCHEDULE = "schedule"
    LOW_STOCK = "low_stock"
    BUDGET_EXCEEDED = "budget_exceeded"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def decimal_column(*, nullable: bool, default: Decimal | None = None) -> Mapped[Decimal | None]:
    return mapped_column(Numeric(12, 2), nullable=nullable, default=default)


jsonb_type = JSONB
status_enum = Enum(CampaignStatus,
                   name = "campaign_status",
                   native_enum = True,
                   values_callable = lambda enum_cls: [item.value for item in enum_cls])
