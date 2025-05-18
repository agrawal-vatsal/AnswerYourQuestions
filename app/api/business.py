from fastapi import APIRouter, HTTPException, Depends
from typing_extensions import Optional

from app.core.dependencies import get_current_user
from app.models.schemas import Business, BusinessCreate
from app.services.business_service import create_business, get_business_by_id

router = APIRouter()


@router.post("/business", response_model=Business)
async def create_business_route(business: BusinessCreate, user=Depends(get_current_user)):
    return await create_business(business.model_dump(exclude_unset=True), user=user)


@router.get("/business/{business_id}", response_model=Business)
async def get_business_route(business_id: str, user=Depends(get_current_user)) -> Optional[
    Business]:
    business: Optional[Business] = await get_business_by_id(business_id, user)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
