from fastapi import APIRouter, HTTPException

from app.models.schemas import Business, BusinessCreate
from app.services.business_service import create_business, get_business_by_id

router = APIRouter()

@router.post("/business", response_model=Business)
async def create_business_route(business: BusinessCreate):
    """
    Create a new business.
    """
    return await create_business(business.model_dump(exclude_unset=True))

@router.get("/business/{business_id}", response_model=Business)
async def get_business_route(business_id: str):
    """
    Get a business by ID.
    """
    business = await get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
