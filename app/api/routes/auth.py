from fastapi import APIRouter, Request
from fastapi.openapi.models import Response

from app.models.schemas import UserCreate
from app.services.auth import create_user, login_user, logout_user

router = APIRouter()

@router.post("/signup")
async def signup_route(user: UserCreate) -> dict:
    await create_user(user)
    return {"detail": "User created successfully"}


@router.post("/login")
async def login_route(user: UserCreate, response: Response) -> dict:
    await login_user(user, response)
    return {"detail": "Login successful"}

@router.post("/logout")
async def logout_route(request: Request, response: Response) -> dict:
    await logout_user(request, response)
    return {"detail": "Logout successful"}
