from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "AnswerYourQuestions")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

user_collection = db.users
business_collection = db.business
business_user_mapping_collection = db.business_user_mapping
file_upload_collection = db.file_uploads
