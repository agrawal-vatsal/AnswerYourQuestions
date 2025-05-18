import logging
from datetime import datetime
from typing import Optional

from bson import ObjectId, errors
from fastapi import HTTPException

from app.constants import UserRole
from app.db.mongo import business_collection, business_user_mapping_collection
from app.models.schemas import Business, User

logger = logging.getLogger(__name__)


async def create_business_user_object(business_id: ObjectId, user_id: ObjectId) -> None:
    business_user_mapping = {
        "business_id": business_id,
        "user_id": user_id,
        "role": UserRole.CREATOR,
        "joined_at": datetime.now(),
    }
    await business_user_mapping_collection.insert_one(business_user_mapping)


async def create_business(business_data: dict, user: User) -> Business:
    result = await business_collection.insert_one(business_data)
    business = {"_id": str(result.inserted_id), **business_data}
    await create_business_user_object(business_id=result.inserted_id, user_id=user.id)
    return Business(**business)


def get_valid_business_for_user_kwargs(user: User) -> dict:
    return {
        "user_id": user.id,
        "$or": [
            {"role": UserRole.CREATOR},
            {"approved_by": {"$exists": True, "$ne": None}},
        ],
    }


async def get_business_by_id(business_id: str, user: User) -> Optional[Business]:
    try:
        business_id = ObjectId(business_id)
    except errors.InvalidId:
        return None

    business = await business_collection.find_one({"_id": ObjectId(business_id)})
    if not business:
        return None

    business_user_mapping = await business_user_mapping_collection.find_one(
        {
            "business_id": business_id,
            **get_valid_business_for_user_kwargs(user),
        }
    )
    if not business_user_mapping:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this business"
        )

    return Business(**business)


async def get_businesses(user: User) -> list[Business]:
    business_user_mapping = await business_user_mapping_collection.find(
        get_valid_business_for_user_kwargs(user)
        ).to_list(length=None)

    if not business_user_mapping:
        return []

    business_ids = [mapping["business_id"] for mapping in business_user_mapping]
    businesses = await business_collection.find({"_id": {"$in": business_ids}}).to_list(length=None)

    return [Business(**business) for business in businesses]
