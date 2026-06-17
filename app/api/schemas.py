import uuid
from datetime import datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.common import CampaignStatus


class CampaignBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    current_status: CampaignStatus = CampaignStatus.ACTIVE
    is_managed: bool = True
    budget_limit: Decimal | None = Field(default=None, ge=0)
    spend_today: Decimal = Field(default=Decimal("0.00"), ge=0)
    stock_days_left: int | None = Field(default=None, ge=0)
    stock_days_min: int | None = Field(default=None, ge=0)
    schedule_enabled: bool = False


class CampaignCreate(CampaignBase):
    target_status: CampaignStatus = CampaignStatus.ACTIVE


class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    current_status: CampaignStatus | None = None
    target_status: CampaignStatus | None = None
    is_managed: bool | None = None
    budget_limit: Decimal | None = Field(default=None, ge=0)
    spend_today: Decimal | None = Field(default=None, ge=0)
    stock_days_left: int | None = Field(default=None, ge=0)
    stock_days_min: int | None = Field(default=None, ge=0)
    schedule_enabled: bool | None = None


class CampaignResponse(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    target_status: CampaignStatus
    created_at: datetime
    updated_at: datetime


class PaginatedCampaigns(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[CampaignResponse]


class ScheduleSlotCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, value: time, info) -> time:
        start_time = info.data.get("start_time")
        if start_time is not None and value <= start_time:
            raise ValueError("end_time must be greater than start_time")
        return value


class ScheduleSlotResponse(ScheduleSlotCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    campaign_id: uuid.UUID


class ScheduleReplaceRequest(BaseModel):
    slots: list[ScheduleSlotCreate]


class EvaluationResponse(BaseModel):
    target_status: CampaignStatus
    triggered_rule: str | None
    rule_details: str


class EvaluateAllItem(BaseModel):
    campaign_id: uuid.UUID
    target_status: CampaignStatus
    triggered_rule: str | None


class EvaluateAllResponse(BaseModel):
    evaluated: int
    results: list[EvaluateAllItem]


class EvaluationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    campaign_id: uuid.UUID
    triggered_rule: str | None
    previous_target: CampaignStatus
    new_target: CampaignStatus
    context: dict
    created_at: datetime


class PaginatedEvaluationLogs(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[EvaluationLogResponse]
