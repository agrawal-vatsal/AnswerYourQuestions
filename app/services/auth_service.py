import uuid
from datetime import datetime

from fastapi import HTTPException

from app.constants import LIFETIME_OF_A_TOKEN
from app.core.security import hash_password, verify_password
from app.db.mongo import user_collection
from app.models.schemas import UserCreate, User


async def create_user(user: UserCreate) -> None:
    if await user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    await user_collection.insert_one({"email": user.email, "password": hashed_password})


async def login_user(user: UserCreate) -> dict:
    db_user: User = await user_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = db_user.get("token")
    token_expiry = db_user.get("token_expiry")
    if token is None or token_expiry < datetime.now():
        token = str(uuid.uuid4())
        token_expiry = datetime.now() + LIFETIME_OF_A_TOKEN
        user_collection.update_one(
            {"email": user.email}, {"$set": {"token": token, "token_expiry": token_expiry}}
        )

    return {"token": token, }


async def logout_user(user: User):
    user_id = user.id
    await user_collection.update_one(
        {"_id": user_id}, {"$set": {"token": None, "token_expiry": None}}
    )
