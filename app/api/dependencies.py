from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.campaign_service import CampaignService


def get_campaign_service(db: Session = Depends(get_db)) -> CampaignService:
    return CampaignService(db)
