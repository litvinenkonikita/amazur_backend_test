from app.models.campaign import Campaign
from app.models.common import CampaignStatus
from app.rules.base import RuleContext, RuleResult


class BudgetExceededRule:
    name = "budget_exceeded"

    def evaluate(self, campaign: Campaign, context: RuleContext) -> RuleResult:
        if campaign.budget_limit is None:
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")
        if campaign.spend_today < campaign.budget_limit:
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")

        return RuleResult(
            matched=True,
            target_status=CampaignStatus.PAUSED,
            rule_name=self.name,
            details=(
                f"Spend today ({campaign.spend_today}) reached or exceeded budget "
                f"limit ({campaign.budget_limit})."
            ),
        )
