from fastapi import APIRouter
from fastapi.params import Depends

from app.core.dependencies import get_current_user
from app.models.schemas import FileUploadCreate, User
from app.services.file_upload_service import upload_file
from app.services.kafka_producer_service import get_kafka_producer_service

router = APIRouter()


@router.post("/upload/{business_id}", response_model=dict)
async def upload_file_route(
        file_data: FileUploadCreate, business_id: str, user: User = Depends(get_current_user),
        kafka_service=Depends(get_kafka_producer_service),
) -> dict:
    """
    Upload a file to the specified business.
    """
    return await upload_file(file_data, business_id, user, kafka_service)
