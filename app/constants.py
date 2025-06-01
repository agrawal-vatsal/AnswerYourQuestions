from datetime import timedelta
from enum import Enum


class UserRole(str, Enum):
    CREATOR = "creator"
    ADMIN = "admin"
    USER = "user"

class FileType(str, Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"


class FileUploadStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"


LIFETIME_OF_A_TOKEN = timedelta(days=7)
