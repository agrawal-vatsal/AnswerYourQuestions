from aiokafka import AIOKafkaProducer
from fastapi import Depends

from app.kafka.producers import get_kafka_producer
from app.kafka.schemas import KafkaFileUploadCreationEvent
from app.kafka.topics import FILE_UPLOADED_TOPIC


class KafkaProducerService:
    def __init__(self, producer):
        self.producer = producer

    async def send_message(self, topic, key, value):
        payload = value.model_dump_json().encode("utf-8")
        await self.producer.send_and_wait(topic, key=key.encode('utf-8'), value=payload)

    async def process_file_upload(self, upload_id: str) -> None:
        """
        Process the file upload by sending a message to Kafka.
        """
        event_data = KafkaFileUploadCreationEvent(
            upload_id=upload_id, source_service="file_upload_service"
        )
        await self.send_message(FILE_UPLOADED_TOPIC, f"file_upload_{upload_id}", event_data)


async def get_kafka_producer_service(producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    return KafkaProducerService(producer)
