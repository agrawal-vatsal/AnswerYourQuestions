from fastapi import FastAPI

from app.api.routes.business import router as business_router

app = FastAPI()
app.include_router(business_router)