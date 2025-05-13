from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_indexes(db: AsyncIOMotorDatabase):
    await db.users.create_index({"email": 1}, unique=True)
    await db.sessions.create_index({"session_id": 1}, unique=True)
    await db.business_user_mapping.create_index({"business_id": 1, "user_id": 1}, unique=True)