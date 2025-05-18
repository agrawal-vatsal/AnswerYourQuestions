from fastapi import FastAPI

from app.api.business import router as business_router
from app.api.auth import router as auth_router

app = FastAPI()
app.include_router(business_router)
app.include_router(auth_router)
