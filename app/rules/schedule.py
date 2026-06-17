from app.models.campaign import Campaign
from app.models.common import CampaignStatus
from app.rules.base import RuleContext, RuleResult
from app.services.schedule_matcher import ScheduleMatcher


class ScheduleRule:
    name = "schedule"

    def evaluate(self, campaign: Campaign, context: RuleContext) -> RuleResult:
        if not campaign.schedule_enabled:
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")
        if ScheduleMatcher.matches(campaign, context.now):
            return RuleResult(matched=False, target_status=None, rule_name=None, details="")

        details = f"Current time {context.now.strftime('%H:%M')} is outside active schedule."
        return RuleResult(
            matched=True,
            target_status=CampaignStatus.PAUSED,
            rule_name=self.name,
            details=details,
        )
