from fastapi import APIRouter

from app.api.routes_campaigns import router as campaigns_router

api_router = APIRouter()
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
