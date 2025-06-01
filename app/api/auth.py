from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.schemas import UserCreate
from app.services.auth_service import create_user, login_user, logout_user

router = APIRouter()


@router.post("/signup")
async def signup_route(user: UserCreate) -> dict:
    await create_user(user)
    return {"detail": "User created successfully"}


@router.post("/login")
async def login_route(user: UserCreate) -> dict:
    token_data = await login_user(user)
    return {"detail": "Login successful", "token": token_data["token"]}


@router.post("/logout")
async def logout_route(user=Depends(get_current_user)) -> dict:
    await logout_user(user)
    return {"detail": "Logged out successfully"}
