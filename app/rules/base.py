from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.models.campaign import Campaign
from app.models.common import CampaignStatus


@dataclass(slots=True)
class RuleContext:
    now: datetime


@dataclass(slots=True)
class RuleResult:
    matched: bool
    target_status: CampaignStatus | None
    rule_name: str | None
    details: str


class Rule(Protocol):
    name: str

    def evaluate(self, campaign: Campaign, context: RuleContext) -> RuleResult: ...
