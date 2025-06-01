from datetime import datetime

from pydantic import BaseModel, Field


class KafkaFileUploadCreationEvent(BaseModel):
    upload_id: str = Field(..., description="Unique identifier for the file upload")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp of the file upload event"
        )
    source_service: str = Field(
        "file_upload_service", description="Service that generated the event"
        )
