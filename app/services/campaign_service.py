import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    CampaignCreate,
    CampaignUpdate,
    EvaluateAllItem,
    EvaluateAllResponse,
    EvaluationResponse,
    ScheduleSlotCreate,
)
from app.models.campaign import Campaign
from app.models.common import RuleName
from app.models.evaluation_log import RuleEvaluationLog
from app.repositories.campaign_repository import CampaignRepository
from app.rules.base import RuleContext
from app.rules.budget_exceeded import BudgetExceededRule
from app.rules.low_stock import LowStockRule
from app.rules.management_disabled import ManagementDisabledRule
from app.rules.schedule import ScheduleRule
from app.services.rule_engine import RuleEngine


class CampaignService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = CampaignRepository(db)
        self.rule_engine = RuleEngine(
            [
                ManagementDisabledRule(),
                ScheduleRule(),
                LowStockRule(),
                BudgetExceededRule(),
            ]
        )

    def create_campaign(self, payload: CampaignCreate) -> Campaign:
        return self.repository.create_campaign(payload)

    def list_campaigns(self, *, limit: int, offset: int, needs_sync: bool | None):
        return self.repository.list_campaigns(limit=limit, offset=offset, needs_sync=needs_sync)

    def get_campaign_or_404(self, campaign_id: uuid.UUID) -> Campaign:
        campaign = self.repository.get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
        return campaign

    def update_campaign(self, campaign_id: uuid.UUID, payload: CampaignUpdate) -> Campaign:
        campaign = self.get_campaign_or_404(campaign_id)
        return self.repository.update_campaign(campaign, payload)

    def replace_schedule(self, campaign_id: uuid.UUID, slots: list[ScheduleSlotCreate]):
        campaign = self.get_campaign_or_404(campaign_id)
        return self.repository.replace_schedule(campaign, slots)

    def get_schedule(self, campaign_id: uuid.UUID):
        campaign = self.get_campaign_or_404(campaign_id)
        return list(campaign.schedules)

    def delete_schedule(self, campaign_id: uuid.UUID) -> None:
        campaign = self.get_campaign_or_404(campaign_id)
        self.repository.delete_schedule(campaign)

    def evaluate_campaign(
        self,
        campaign_id: uuid.UUID,
        *,
        dry_run: bool,
        now: datetime | None = None,
    ) -> EvaluationResponse:
        campaign = self.get_campaign_or_404(campaign_id)
        return self._evaluate_single_campaign(campaign, dry_run=dry_run, now=now)

    def evaluate_all(self, *, now: datetime | None = None) -> EvaluateAllResponse:
        campaigns = self.repository.list_managed_campaigns()
        results: list[EvaluateAllItem] = []
        for campaign in campaigns:
            evaluation = self._evaluate_single_campaign(campaign, dry_run=False, now=now)
            results.append(
                EvaluateAllItem(
                    campaign_id=campaign.id,
                    target_status=evaluation.target_status,
                    triggered_rule=evaluation.triggered_rule,
                )
            )
        return EvaluateAllResponse(evaluated=len(results), results=results)

    def list_logs(self, campaign_id: uuid.UUID, *, limit: int, offset: int):
        self.get_campaign_or_404(campaign_id)
        return self.repository.list_logs(campaign_id=campaign_id, limit=limit, offset=offset)

    def _evaluate_single_campaign(
        self,
        campaign: Campaign,
        *,
        dry_run: bool,
        now: datetime | None,
    ) -> EvaluationResponse:
        previous_target = campaign.target_status
        result = self.rule_engine.evaluate(campaign, RuleContext(now=now or datetime.utcnow()))

        if result.rule_name == RuleName.MANAGEMENT_DISABLED:
            new_target = previous_target
        else:
            new_target = result.target_status

        context_snapshot = self._build_context_snapshot(campaign, now=now)

        if not dry_run:
            campaign.target_status = new_target
            self.db.add(campaign)
            self.db.flush()
            self.db.add(
                RuleEvaluationLog(
                    campaign_id=campaign.id,
                    triggered_rule=result.rule_name,
                    previous_target=previous_target,
                    new_target=new_target,
                    context=context_snapshot,
                )
            )
            self.db.commit()
            self.db.refresh(campaign)
        else:
            self.db.rollback()

        return EvaluationResponse(
            target_status=new_target,
            triggered_rule=result.rule_name,
            rule_details=result.details,
        )

    @staticmethod
    def _build_context_snapshot(campaign: Campaign, *, now: datetime | None) -> dict:
        effective_now = now or datetime.utcnow()
        return {
            "evaluated_at": effective_now.isoformat(),
            "campaign": {
                "id": str(campaign.id),
                "name": campaign.name,
                "current_status": campaign.current_status.value,
                "target_status": campaign.target_status.value,
                "is_managed": campaign.is_managed,
                "budget_limit": str(campaign.budget_limit) if campaign.budget_limit is not None else None,
                "spend_today": str(campaign.spend_today),
                "stock_days_left": campaign.stock_days_left,
                "stock_days_min": campaign.stock_days_min,
                "schedule_enabled": campaign.schedule_enabled,
                "schedule_slots": [
                    {
                        "id": str(slot.id),
                        "day_of_week": slot.day_of_week,
                        "start_time": slot.start_time.isoformat(),
                        "end_time": slot.end_time.isoformat(),
                    }
                    for slot in campaign.schedules
                ],
            },
        }
