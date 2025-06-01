from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Answer Your Questions"
    DEBUG: bool = True

    KAFKA_BOOTSTRAP_SERVERS: str = ["localhost:9092"]
    KAFKA_CONSUMER_GROUP_ID: str = "fastapi-app-consumer_group"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()