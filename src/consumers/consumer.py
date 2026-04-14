import json
import uuid
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from src.constants import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from src.data.models.message import Message
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
                topic_name = message.topic

                raw_data = message.value.decode("utf-8")
                print("msg: " + str(raw_data), "topic: " + topic_name)
                decoded_msg = json.loads(raw_data)

                id = UUID(decoded_msg.get("to_user"))
                text = str(await create_message(decoded_msg))

                await insert_message(Message(id=uuid.uuid4(), text=text, user_id=id))
                await send(id, text)
                await consumer.commit()

            except Exception as e:
                print(e)
    finally:
        await consumer.stop()
