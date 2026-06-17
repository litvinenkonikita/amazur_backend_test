from app.models.campaign import Campaign
from app.rules.base import RuleContext, RuleResult


class ManagementDisabledRule:
    name = "management_disabled"

    def evaluate(self, campaign: Campaign, context: RuleContext) -> RuleResult:
        if campaign.is_managed:
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")
        return RuleResult(
            matched=True,
            target_status=campaign.target_status,
            rule_name=self.name,
            details="Automatic management is disabled; target_status is unchanged.",
        )
