import logging
import uuid
from collections.abc import Awaitable, Callable, Mapping
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from src.constants import (
    ADMIN_CANCEL_TOPIC,
    ADMIN_UPDATE_TOPIC,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_GROUP_ID,
    MESSAGES_TOPIC_END,
    USER_BOOK_TOPIC,
    USER_CANCEL_TOPIC,
)
from src.data.models.message import Message
from src.data.models.send import Send
from src.repositories.message_repository import insert_message
from src.repositories.send_repository import get_send_by_hash, insert_send
from src.services.connection_service import send
from src.services.messages_service import (
    create_admin_cancel_message,
    create_admin_update_message,
    create_message,
    create_messages_message_end,
    create_messages_message_start,
    create_user_book_message,
    create_user_cancel_message,
)


async def matching(topic: str) -> Callable[[Mapping[str, str | None]], Awaitable[Message]]:
    if topic == USER_BOOK_TOPIC:
        return create_user_book_message
    if topic == USER_CANCEL_TOPIC:
        return create_user_cancel_message
    if topic == ADMIN_CANCEL_TOPIC:
        return create_admin_cancel_message
    if topic == ADMIN_UPDATE_TOPIC:
        return create_admin_update_message
    if topic == MESSAGES_TOPIC_END:
        return create_messages_message_end
    return create_messages_message_start


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
                hash_ms = hash(msg)
                snd = await get_send_by_hash(str(hash_ms))
                if snd is not None:
                    continue
                send_ms = Send(uuid.uuid4(), str(hash_ms))
                await insert_send(send_ms)
                await insert_message(msg)
                await send(UUID(str(msg.user_id)), msg)
                await consumer.commit()

            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    finally:
        await consumer.stop()
