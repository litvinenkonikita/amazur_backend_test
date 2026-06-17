import uuid

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_campaign_service
from app.api.schemas import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    EvaluateAllResponse,
    EvaluationResponse,
    PaginatedCampaigns,
    PaginatedEvaluationLogs,
    ScheduleReplaceRequest,
    ScheduleSlotResponse,
)
from app.services.campaign_service import CampaignService

router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: CampaignCreate,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.model_validate(service.create_campaign(payload))


@router.get("", response_model=PaginatedCampaigns)
def list_campaigns(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    needs_sync: bool | None = Query(default=None),
    service: CampaignService = Depends(get_campaign_service),
) -> PaginatedCampaigns:
    total, items = service.list_campaigns(limit=limit, offset=offset, needs_sync=needs_sync)
    return PaginatedCampaigns(
        total=total,
        limit=limit,
        offset=offset,
        items=[CampaignResponse.model_validate(item) for item in items],
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.model_validate(service.get_campaign_or_404(campaign_id))


@router.patch("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: uuid.UUID,
    payload: CampaignUpdate,
    service: CampaignService = Depends(get_campaign_service),
) -> CampaignResponse:
    return CampaignResponse.model_validate(service.update_campaign(campaign_id, payload))


@router.put("/{campaign_id}/schedule", response_model=list[ScheduleSlotResponse])
def replace_schedule(
    campaign_id: uuid.UUID,
    payload: ScheduleReplaceRequest,
    service: CampaignService = Depends(get_campaign_service),
) -> list[ScheduleSlotResponse]:
    slots = service.replace_schedule(campaign_id, payload.slots)
    return [ScheduleSlotResponse.model_validate(slot) for slot in slots]


@router.get("/{campaign_id}/schedule", response_model=list[ScheduleSlotResponse])
def get_schedule(
    campaign_id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> list[ScheduleSlotResponse]:
    slots = service.get_schedule(campaign_id)
    return [ScheduleSlotResponse.model_validate(slot) for slot in slots]


@router.delete("/{campaign_id}/schedule", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    campaign_id: uuid.UUID,
    service: CampaignService = Depends(get_campaign_service),
) -> Response:
    service.delete_schedule(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{campaign_id}/evaluate", response_model=EvaluationResponse)
def evaluate_campaign(
    campaign_id: uuid.UUID,
    dry_run: bool = Query(default=False),
    service: CampaignService = Depends(get_campaign_service),
) -> EvaluationResponse:
    return service.evaluate_campaign(campaign_id, dry_run=dry_run)


@router.post("/evaluate-all", response_model=EvaluateAllResponse)
def evaluate_all(
    service: CampaignService = Depends(get_campaign_service),
) -> EvaluateAllResponse:
    return service.evaluate_all()


@router.get("/{campaign_id}/evaluation-history", response_model=PaginatedEvaluationLogs)
def evaluation_history(
    campaign_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: CampaignService = Depends(get_campaign_service),
) -> PaginatedEvaluationLogs:
    total, items = service.list_logs(campaign_id, limit=limit, offset=offset)
    return PaginatedEvaluationLogs(total=total, limit=limit, offset=offset, items=items)
