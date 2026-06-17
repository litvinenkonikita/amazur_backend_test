import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.schemas import CampaignCreate, CampaignUpdate, ScheduleSlotCreate
from app.models.campaign import Campaign
from app.models.campaign_schedule import CampaignSchedule
from app.models.evaluation_log import RuleEvaluationLog


class CampaignRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_campaign(self, payload: CampaignCreate) -> Campaign:
        campaign = Campaign(**payload.model_dump())
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def list_campaigns(
        self,
        *,
        limit: int,
        offset: int,
        needs_sync: bool | None,
    ) -> tuple[int, list[Campaign]]:
        stmt = select(Campaign).options(selectinload(Campaign.schedules)).order_by(Campaign.created_at.desc())
        count_stmt = select(func.count()).select_from(Campaign)

        if needs_sync is True:
            sync_filter = Campaign.current_status != Campaign.target_status
            stmt = stmt.where(sync_filter)
            count_stmt = count_stmt.where(sync_filter)

        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.offset(offset).limit(limit)).unique())
        return total, items

    def get_campaign(self, campaign_id: uuid.UUID) -> Campaign | None:
        stmt = (
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(selectinload(Campaign.schedules))
        )
        return self.db.scalar(stmt)

    def update_campaign(self, campaign: Campaign, payload: CampaignUpdate) -> Campaign:
        data = payload.model_dump(exclude_unset=True)
        for field_name, value in data.items():
            setattr(campaign, field_name, value)
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def replace_schedule(self, campaign: Campaign, slots: list[ScheduleSlotCreate]) -> list[CampaignSchedule]:
        campaign.schedules.clear()
        self.db.flush()
        for slot in slots:
            campaign.schedules.append(CampaignSchedule(**slot.model_dump()))
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return list(campaign.schedules)

    def delete_schedule(self, campaign: Campaign) -> None:
        campaign.schedules.clear()
        self.db.add(campaign)
        self.db.commit()

    def list_logs(
        self,
        *,
        campaign_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> tuple[int, list[RuleEvaluationLog]]:
        base = select(RuleEvaluationLog).where(RuleEvaluationLog.campaign_id == campaign_id)
        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        items = list(
            self.db.scalars(
                base.order_by(RuleEvaluationLog.created_at.desc()).offset(offset).limit(limit),
            )
        )
        return total, items

    def list_managed_campaigns(self) -> list[Campaign]:
        stmt = (
            select(Campaign)
            .where(Campaign.is_managed.is_(True))
            .options(selectinload(Campaign.schedules))
            .order_by(Campaign.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique())

    def add_evaluation_log(self, log: RuleEvaluationLog) -> RuleEvaluationLog:
        self.db.add(log)
        self.db.commit()
        self.refresh_instance(log)
        return log

    def commit(self) -> None:
        self.db.commit()

    def refresh_instance(self, instance: object) -> None:
        self.db.refresh(instance)
