import uuid
from datetime import datetime

from fastapi import HTTPException, Request
from fastapi.openapi.models import Response

from app.constants import LIFETIME_OF_A_SESSION
from app.core.security import hash_password, verify_password
from app.db.mongo import db
from app.models.schemas import UserCreate


async def create_user(user: UserCreate) -> None:
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    await db.users.insert_one({"email": user.email, "password": hashed_password})

async def login_user(user: UserCreate, response: Response):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    session_data = {
        "user_id": db_user["_id"],
        "session_id": str(uuid.uuid4()),
        "expired_at": datetime.now() + LIFETIME_OF_A_SESSION
    }
    await db.sessions.insert_one(session_data)
    response.set_cookie(key="session_id", value=session_data["session_id"], httponly=True, secure=True, samesite="Lax")

async def logout_user(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        await db.sessions.delete_one({"session_id": session_id})
        response.delete_cookie(key="session_id")

