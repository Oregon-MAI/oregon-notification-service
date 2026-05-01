import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from src.constants import (
    ADMIN_CANCEL_TOPIC,
    ADMIN_UPDATE_TOPIC,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    USER_BOOK_TOPIC,
    USER_CANCEL_TOPIC,
)
from src.data.models.message import Message
from src.repositories.message_repository import insert_message
from src.services.connection_service import send
from src.services.messages_service import (
    create_admin_cancel_message,
    create_admin_update_message,
    create_message,
    create_messages_message,
    create_user_book_message,
    create_user_cancel_message,
)


async def matching(topic: str) -> Callable[[dict], Awaitable[Message]]:
    if topic == USER_BOOK_TOPIC:
        return create_user_book_message
    if topic == USER_CANCEL_TOPIC:
        return create_user_cancel_message
    if topic == ADMIN_CANCEL_TOPIC:
        return create_admin_cancel_message
    if topic == ADMIN_UPDATE_TOPIC:
        return create_admin_update_message
    return create_messages_message


async def consume(topic: str) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    return consumer


async def cons(topic: str) -> None:
    logging.info("topic: %s.", topic)
    consumer = await consume(topic)
    msg_parser = await matching(topic)
    try:
        async for message in consumer:
            try:
                msg = await create_message(message, msg_parser)
                await insert_message(msg)
                await send(UUID(str(msg.user_id)), msg)
                await consumer.commit()

            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    finally:
        await consumer.stop()
