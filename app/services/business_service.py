import logging
from datetime import datetime
from typing import Optional, List

from bson import ObjectId, errors
from fastapi import HTTPException

from app.constants import UserRole
from app.db.mongo import business_collection, business_user_mapping_collection
from app.models.schemas import Business, User, BusinessUserMapping

logger = logging.getLogger(__name__)


async def create_business_user_object(business_id: ObjectId, user_id: ObjectId) -> None:
    """Create a business user mapping with creator role."""
    business_user_mapping = {
        "business_id": business_id,
        "user_id": user_id,
        "role": UserRole.CREATOR,
        "joined_at": datetime.now(),
    }
    await business_user_mapping_collection.insert_one(business_user_mapping)


async def create_business(business_data: dict, user: User) -> Business:
    """Create a new business and link it to the creator user."""
    result = await business_collection.insert_one(business_data)
    business_id = result.inserted_id

    # Create the business user mapping in parallel
    await create_business_user_object(business_id=business_id, user_id=user.id)

    # Format and return the business object
    business = {"_id": str(business_id), **business_data}
    return Business(**business)


def get_valid_business_for_user_kwargs(user: User) -> dict:
    """Get query parameters for validating a user's access to a business."""
    return {
        "user_id": user.id,
        "$or": [
            {"role": UserRole.CREATOR},
            {"approved_by": {"$exists": True, "$ne": None}},
        ],
    }


async def get_business_by_id(business_id: str, user: User) -> Optional[Business]:
    """Get a business by ID if the user has access to it."""
    # Validate business_id
    try:
        business_id = ObjectId(business_id)
    except errors.InvalidId:
        return None

    business = await business_collection.find_one({"_id": ObjectId(business_id)})
    if not business:
        return None

    mapping_obj = {
        "business_id": business_id,
        **get_valid_business_for_user_kwargs(user),
    }

    business_user_mapping = await business_user_mapping_collection.find_one(mapping_obj)
    if not business_user_mapping:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this business"
        )

    return Business(**business)


async def get_businesses(user: User) -> List[Business]:
    """Get all businesses that the user has access to."""
    # Get all business mappings for this user
    mapping_query = get_valid_business_for_user_kwargs(user)
    business_user_mappings = await business_user_mapping_collection.find(mapping_query).to_list(length=None)

    if not business_user_mappings:
        return []

    # Extract business IDs and fetch businesses
    business_ids = [mapping["business_id"] for mapping in business_user_mappings]
    businesses_query = {"_id": {"$in": business_ids}}
    businesses = await business_collection.find(businesses_query).to_list(length=None)

    # Convert to Business objects
    return [Business(**business) for business in businesses]


async def search_businesses(query: str) -> List[Business]:
    """Search for businesses by name using case-insensitive regex."""
    search_query = {"name": {"$regex": query, "$options": "i"}}
    businesses = await business_collection.find(search_query).to_list(length=None)

    return [Business(**business) for business in businesses]


async def join_business_request(business_id: str, user: User, role: UserRole) -> None:
    """Request to join a business with a specific role."""
    # Validate business_id
    try:
        object_id = ObjectId(business_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid business ID")

    # Check if user is already a member or has a pending request
    existing_mapping = await business_user_mapping_collection.find_one(
        {"business_id": object_id, "user_id": user.id}
    )

    if existing_mapping:
        raise HTTPException(
            status_code=400,
            detail="Already a member of this business or request already raised"
        )

    # Create the join request
    business_user_mapping = {
        "business_id": object_id,
        "user_id": user.id,
        "role": role,
        "joined_at": datetime.now(),
    }
    await business_user_mapping_collection.insert_one(business_user_mapping)


async def get_business_requests(business_id: str, user: User) -> List[BusinessUserMapping]:
    """Get all pending join requests for a business."""
    # Validate business_id
    try:
        object_id = ObjectId(business_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid business ID")

    # Check if business exists
    business = await business_collection.find_one({"_id": object_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    # Check if user has permission to view requests
    permission_query = {
        "business_id": object_id,
        "user_id": user.id,
        "$or": [
            {"role": UserRole.CREATOR},
            {"approved_by": {"$exists": True, "$ne": None}, "role": UserRole.ADMIN},
        ],
    }

    has_permission = await business_user_mapping_collection.find_one(permission_query)
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to approve business requests"
        )

    # Get all pending requests
    requests_query = {
        "business_id": object_id,
        "role": {"$ne": UserRole.CREATOR},
        "$or": [
            {"approved_by": None},
            {"approved_by": {"$exists": False}}
        ],
    }

    requests = await business_user_mapping_collection.find(requests_query).to_list(length=None)

    return [BusinessUserMapping(**request) for request in requests]


async def approve_business_request(business_id: str, user_id: str, current_user: User) -> None:
    """Approve a user's request to join a business."""
    # Validate IDs
    try:
        business_oid = ObjectId(business_id)
        user_oid = ObjectId(user_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid business ID or user ID")

    # Verify business exists
    business = await business_collection.find_one({"_id": business_oid})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    # Check if current user has permission to approve requests
    permission_query = {
        "business_id": business_oid,
        "user_id": current_user.id,
        "$or": [
            {"role": UserRole.CREATOR},
            {"approved_by": {"$exists": True, "$ne": None}, "role": UserRole.ADMIN},
        ],
    }

    has_permission = await business_user_mapping_collection.find_one(permission_query)
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to approve business requests"
        )

    # Approve the request
    await business_user_mapping_collection.update_one(
        {"business_id": business_oid, "user_id": user_oid},
        {"$set": {"approved_by": current_user.id}}
    )
