from fastapi import APIRouter, HTTPException, Depends
from typing_extensions import Optional

from app.constants import UserRole
from app.core.dependencies import get_current_user
from app.models.schemas import Business, BusinessCreate, BusinessUserMapping
from app.services.business_service import (
    create_business, get_business_by_id, get_businesses,
    search_businesses, join_business_request, get_business_requests, approve_business_request,
)

router = APIRouter()


@router.post("/business", response_model=Business)
async def create_business_route(business: BusinessCreate, user=Depends(get_current_user)):
    return await create_business(business.model_dump(exclude_unset=True), user=user)


@router.get("/business", response_model=list[Business])
async def get_businesses_route(user=Depends(get_current_user)) -> list[Business]:
    return await get_businesses(user)


@router.get("/business/{business_id}", response_model=Business)
async def get_business_route(business_id: str, user=Depends(get_current_user)) -> Optional[
    Business]:
    business: Optional[Business] = await get_business_by_id(business_id, user)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.get("/business/search", response_model=list[Business])
async def search_business_route(query: str) -> list[Business]:
    business: list[Business] = await search_businesses(query)
    if not business:
        raise HTTPException(status_code=404, detail="No businesses found")

    return business


@router.post("/business/join/{business_id}/{role}", response_model=dict)
async def join_business_route(
        business_id: str, role: UserRole, user=Depends(get_current_user),
) -> dict:
    await join_business_request(business_id, user, role)
    return {"detail": "Join request sent successfully"}


@router.get("/business/join_requests/{business_id}", response_model=list[BusinessUserMapping])
async def get_join_requests_route(business_id: str, user=Depends(get_current_user)) -> list[
    BusinessUserMapping]:
    requests = await get_business_requests(business_id, user)
    if not requests:
        raise HTTPException(status_code=404, detail="No join requests found")

    return requests


@router.post("/business/join_requests/{business_id}/accept/{user_id}", response_model=dict)
async def accept_join_request_route(
        business_id: str, user_id: str, user=Depends(get_current_user),
) -> dict:
    await approve_business_request(business_id, user_id, user)
    return {"detail": "Join request accepted successfully"}
