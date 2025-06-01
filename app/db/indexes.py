from app.db.mongo import user_collection, business_user_mapping_collection


async def create_indexes():
    await user_collection.create_index({"email": 1}, unique=True)
    await business_user_mapping_collection.create_index(
        {"business_id": 1, "user_id": 1}, unique=True
        )
