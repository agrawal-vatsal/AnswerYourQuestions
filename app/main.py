# app/main.py
from fastapi import FastAPI
from app.api.business import router as business_router
from app.api.auth import router as auth_router
from app.db.indexes import create_indexes

app = FastAPI(
    title="AnswerYourQuestions API",
    description="API for Question and Answer service",
    version="0.1.0"
)


@app.on_event("startup")
async def startup_db_client():
    await create_indexes()


app.include_router(business_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}