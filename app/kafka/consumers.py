import asyncio
import json

from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.kafka.schemas import KafkaFileUploadCreationEvent
from app.kafka.topics import FILE_UPLOADED_TOPIC
from app.services.file_upload_service import process_file_upload


async def start_kafka_consumers():
    consumer = AIOKafkaConsumer(
        FILE_UPLOADED_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID,
        auto_offset_reset="latest"
    )

    await consumer.start()

    try:
        async for message in consumer:
            try:
                decoded_value = json.loads(message.value.decode("utf-8"))
                if message.topic == FILE_UPLOADED_TOPIC:
                    # Process the file upload event
                    event = KafkaFileUploadCreationEvent(**decoded_value)
                    await process_file_upload(event.upload_id)
            except Exception as e:
                print(f"Error processing message: {e}, message: {message}")
    except asyncio.CancelledError:
        print("Kafka consumer stopped")
    except Exception as e:
        print(f"Error in Kafka consumer: {e}")
    finally:
        await consumer.stop()
