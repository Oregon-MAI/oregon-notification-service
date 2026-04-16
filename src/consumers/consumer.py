import json
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from src.constants import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from src.repositories.message_repository import insert_message
from src.services.connection_service import send
from src.services.messages_service import create_message


async def consume(topic: list[str]) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        *topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    return consumer


async def cons(topic: list[str]) -> None:
    print("topic: ", topic)
    consumer = await consume(topic)
    try:
        async for message in consumer:
            try:
                raw_data = message.value.decode("utf-8")
                msg = await create_message(json.loads(raw_data))
                await insert_message(msg)
                await send(UUID(str(msg.user_id)), str(msg.text))
                await consumer.commit()

            except Exception as e:
                print(e)
    finally:
        await consumer.stop()
