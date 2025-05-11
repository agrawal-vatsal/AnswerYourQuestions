import logging
from typing import Optional

from bson import ObjectId, errors

from app.db.mongo import db
from app.models.schemas import Business

logger = logging.getLogger(__name__)

async def create_business(business_data: dict) -> Business:
    """
    Create a new business in the database.

    Args:
        business_data (dict): The data for the new business.

    Returns:
        Business: The created business object.
    """
    result = await db.business.insert_one(business_data)
    business = await db.business.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for Pydantic model
    if business and "_id" in business:
        business["_id"] = str(business["_id"])

    logger.info(f"Data is {business} with {business_data}")

    return Business(**business)

async def get_business_by_id(business_id: str) -> Optional[Business]:
    """
    Get a business by its ID.

    Args:
        business_id (str): The ID of the business to retrieve.

    Returns:
        Business: The business object.
    """
    try:
        business_id = ObjectId(business_id)
    except errors.InvalidId:
        return None

    business = await db.business.find_one({"_id": ObjectId(business_id)})
    return Business(**business) if business else None