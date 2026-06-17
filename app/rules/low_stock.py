from app.models.campaign import Campaign
from app.models.common import CampaignStatus
from app.rules.base import RuleContext, RuleResult


class LowStockRule:
    name = "low_stock"

    def evaluate(self, campaign: Campaign, context: RuleContext) -> RuleResult:
        if campaign.stock_days_min is None or campaign.stock_days_left is None:
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")
        if campaign.stock_days_left >= campaign.stock_days_min:
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")

        return RuleResult(
            matched=True,
            target_status=CampaignStatus.PAUSED,
            rule_name=self.name,
            details=(
                f"Stock days left ({campaign.stock_days_left}) is below minimum "
                f"threshold ({campaign.stock_days_min})."
            ),
        )
