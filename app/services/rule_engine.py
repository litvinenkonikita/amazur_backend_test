from app.models.campaign import Campaign
from app.models.common import CampaignStatus
from app.rules.base import Rule, RuleContext, RuleResult


class RuleEngine:
    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules

    def evaluate(self, campaign: Campaign, context: RuleContext) -> RuleResult:
        for rule in self.rules:
            result = rule.evaluate(campaign, context)
            if result.matched:
                return result
        return RuleResult(
            matched=True,
            target_status=CampaignStatus.ACTIVE,
            rule_name=None,
            details="No rules matched; target_status is active.",
        )
