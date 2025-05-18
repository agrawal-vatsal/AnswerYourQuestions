from datetime import datetime

from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader

from app.db.mongo import db
from app.models.schemas import User

api_key_header = APIKeyHeader(name="Authorization")


async def get_current_user(authorization: str = Depends(api_key_header)) -> User:
    if not authorization or not authorization.startswith("Token "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    token = authorization.split(" ")[1]
    user = await db.users.find_one({"token": token})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    if user.get("token_expiry") and user.get("token_expiry") < datetime.now():
        raise HTTPException(status_code=401, detail="Token expired")

    return User(**user)
