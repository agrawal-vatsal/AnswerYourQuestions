import asyncio

from app.kafka.consumers import start_kafka_consumers
from app.kafka.producers import kafka_producer_instance, create_kafka_producer

background_tasks = set()


async def startup_event():
    global kafka_producer_instance
    kafka_producer_instance = await create_kafka_producer()
    await kafka_producer_instance.start()

    consumer_task = asyncio.create_task(start_kafka_consumers())
    background_tasks.add(consumer_task)

    consumer_task.add_done_callback(background_tasks.discard)


async def shutdown_event():
    if kafka_producer_instance:
        await kafka_producer_instance.stop()

    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)
