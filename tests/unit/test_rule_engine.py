from datetime import datetime, time
from decimal import Decimal
from uuid import uuid4

from app.models.campaign import Campaign
from app.models.campaign_schedule import CampaignSchedule
from app.models.common import CampaignStatus
from app.rules.base import RuleContext
from app.rules.budget_exceeded import BudgetExceededRule
from app.rules.low_stock import LowStockRule
from app.rules.management_disabled import ManagementDisabledRule
from app.rules.schedule import ScheduleRule
from app.services.rule_engine import RuleEngine


def make_campaign(**overrides) -> Campaign:
    payload = {
        "id": uuid4(),
        "name": "Campaign",
        "current_status": CampaignStatus.ACTIVE,
        "target_status": CampaignStatus.ACTIVE,
        "is_managed": True,
        "budget_limit": None,
        "spend_today": Decimal("0.00"),
        "stock_days_left": None,
        "stock_days_min": None,
        "schedule_enabled": False,
    }
    payload.update(overrides)
    campaign = Campaign(**payload)
    campaign.schedules = overrides.get("schedules", [])
    return campaign


def make_slot(day_of_week: int, start: str, end: str) -> CampaignSchedule:
    start_time = time.fromisoformat(start)
    end_time = time.fromisoformat(end)
    return CampaignSchedule(id=uuid4(), campaign_id=uuid4(), day_of_week=day_of_week, start_time=start_time, end_time=end_time)


def test_management_disabled_keeps_target_status_unchanged() -> None:
    engine = RuleEngine([ManagementDisabledRule(), ScheduleRule(), LowStockRule(), BudgetExceededRule()])
    campaign = make_campaign(is_managed=False, target_status=CampaignStatus.PAUSED)

    result = engine.evaluate(campaign, RuleContext(now=datetime(2026, 6, 17, 12, 0)))

    assert result.rule_name == "management_disabled"
    assert result.target_status == CampaignStatus.PAUSED


def test_schedule_rule_has_priority_over_budget_rule() -> None:
    engine = RuleEngine([ManagementDisabledRule(), ScheduleRule(), LowStockRule(), BudgetExceededRule()])
    campaign = make_campaign(
        schedule_enabled=True,
        budget_limit=Decimal("1000.00"),
        spend_today=Decimal("1500.00"),
        schedules=[make_slot(2, "09:00", "21:00")],
    )

    result = engine.evaluate(campaign, RuleContext(now=datetime(2026, 6, 17, 22, 30)))

    assert result.rule_name == "schedule"
    assert result.target_status == CampaignStatus.PAUSED


def test_budget_limit_equal_to_spend_pauses_campaign() -> None:
    rule = BudgetExceededRule()
    campaign = make_campaign(budget_limit=Decimal("1000.00"), spend_today=Decimal("1000.00"))

    result = rule.evaluate(campaign, RuleContext(now=datetime(2026, 6, 17, 10, 0)))

    assert result.rule_name == "budget_exceeded"
    assert result.target_status == CampaignStatus.PAUSED


def test_time_on_schedule_start_boundary_is_active() -> None:
    rule = ScheduleRule()
    campaign = make_campaign(schedule_enabled=True, schedules=[make_slot(2, "09:00", "21:00")])

    result = rule.evaluate(campaign, RuleContext(now=datetime(2026, 6, 17, 9, 0)))

    assert result.matched is False


def test_time_on_schedule_end_boundary_is_paused() -> None:
    rule = ScheduleRule()
    campaign = make_campaign(schedule_enabled=True, schedules=[make_slot(2, "09:00", "21:00")])

    result = rule.evaluate(campaign, RuleContext(now=datetime(2026, 6, 17, 21, 0)))

    assert result.rule_name == "schedule"
    assert result.target_status == CampaignStatus.PAUSED


def test_low_stock_pauses_campaign() -> None:
    rule = LowStockRule()
    campaign = make_campaign(stock_days_min=5, stock_days_left=3)

    result = rule.evaluate(campaign, RuleContext(now=datetime(2026, 6, 17, 10, 0)))

    assert result.rule_name == "low_stock"
    assert result.target_status == CampaignStatus.PAUSED
