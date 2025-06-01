from aiokafka import AIOKafkaProducer

from app.core.config import settings

kafka_producer_instance: AIOKafkaProducer | None = None


async def get_kafka_producer() -> AIOKafkaProducer:
    if kafka_producer_instance is None:
        raise Exception("Kafka producer not initialized")
    return kafka_producer_instance


async def create_kafka_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        client_id="fastapi-app-producer",
    )

    return producer
