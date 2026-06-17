from datetime import datetime

from app.models.campaign import Campaign
from app.models.campaign_schedule import CampaignSchedule


class ScheduleMatcher:
    @staticmethod
    def matches(campaign: Campaign, now: datetime) -> bool:
        if not campaign.schedule_enabled:
            return True
        weekday = now.weekday()
        current_time = now.time()
        return any(
            ScheduleMatcher._is_active_slot(slot, weekday, current_time)
            for slot in campaign.schedules
        )

    @staticmethod
    def _is_active_slot(slot: CampaignSchedule, weekday: int, current_time) -> bool:
        return (
            slot.day_of_week == weekday
            and slot.start_time <= current_time < slot.end_time
        )
