from fastapi import APIRouter
from fastapi.params import Depends

from app.core.dependencies import get_current_user
from app.models.schemas import FileUploadCreate

router = APIRouter()

@router.post("/upload/{business_id}", response_model=dict)
def upload_file(file_data: FileUploadCreate, business_id: str, user=Depends(get_current_user)) -> dict:
    """
    Upload a file to the specified business.
    """
