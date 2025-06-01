from fastapi import HTTPException

from app.db.mongo import business_user_mapping_collection, file_upload_collection
from app.models.schemas import FileUploadCreate, User


async def upload_file(
        file_data: FileUploadCreate, business_id: str, user: User, kafka_service,
) -> dict:
    """
    Upload a file to the specified business.
    """
    business_user_mapping = business_user_mapping_collection.find_one(
        {
            "business_id": business_id, "user_id": user.id,
            "$or": [{"role": "CREATOR"}, {"approved_by": {"$exists": True, "$ne": None}}],
        }
    )

    if not business_user_mapping:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to upload files to this business"
        )

    uploaded_file = file_upload_collection.insert_one(
        {"business_id": business_id, "user_id": user.id, **file_data.model_dump()}
    )

    kafka_service.process_file_upload(uploaded_file.inserted_id)

    return {
        "message": "File uploaded successfully",
    }


async def process_file_upload(upload_id: str) -> None:
    pass
