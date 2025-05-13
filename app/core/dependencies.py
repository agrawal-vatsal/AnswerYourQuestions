from datetime import datetime

from fastapi import Request, HTTPException

from app.db.mongo import db
from app.models.schemas import User


async def get_current_user(request: Request) -> User:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = await db.sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session["expired_at"] < datetime.now():
        raise HTTPException(status_code=401, detail="Session expired")

    user = await db.users.find_one({"_id": session["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return User(**user)
