from datetime import datetime
from typing import Optional, Any

from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler, EmailStr, constr, FileUrl
from pydantic_core import core_schema

from app.constants import UserRole, FileType, FileUploadStatus


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v: str, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, _handler):
        return {"type": "string"}


class BusinessCreate(BaseModel):
    name: str


class Business(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    token: Optional[constr(min_length=36, max_length=36)]
    token_expiry: Optional[datetime]

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }


class BusinessUserMapping(BaseModel):
    user_id: PyObjectId
    business_id: PyObjectId
    role: UserRole
    joined_at: datetime
    approved_by: Optional[PyObjectId] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }

class FileUploadCreate(BaseModel):
    file_url: FileUrl
    file_type: FileType

class FileUpload(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    file_url: FileUrl
    file_type: FileType
    status: FileUploadStatus = Field(default=FileUploadStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    business_id: PyObjectId
    user_id: PyObjectId

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }
