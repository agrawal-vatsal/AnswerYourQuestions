from datetime import timedelta
from enum import Enum


class UserRole(str, Enum):
    CREATOR = "creator"
    ADMIN = "admin"
    USER = "user"


LIFETIME_OF_A_TOKEN = timedelta(days=7)
