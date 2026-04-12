import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from uuid import UUID
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI

from src.data.models.message import Message
from src.repositories.message_repository import insert_message
from src.services.connection_service import send
from src.constants import KAFKA_GROUP_ID, CONSUME_TOPICS, KAFKA_BOOTSTRAP_SERVERS
from src.services.messages_service import create_message

@asynccontextmanager
async def background(app: FastAPI):
    tasks = [
        asyncio.create_task(background_task()),
    ]
    yield
    for task in tasks:
        task.cancel()

async def start_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        *CONSUME_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
    )
    print(KAFKA_BOOTSTRAP_SERVERS, CONSUME_TOPICS)
    await consumer.start()
    return consumer

async def background_task() -> None:
    consumer = await start_consumer()
    try:
        async for message in consumer:
            try:
                topic_name = message.topic

                #добавить обработку сообщений в зависимости от топика
                if(topic_name == CONSUME_TOPICS[0]):
                    pass
                elif topic_name == CONSUME_TOPICS[1]:
                    pass
                elif topic_name == CONSUME_TOPICS[2]:
                    pass
                elif topic_name == CONSUME_TOPICS[3]:
                    pass
                elif topic_name == CONSUME_TOPICS[4]:
                    pass

                raw_data = message.value.decode('utf-8')
                print('msg: ' + str(raw_data),'topic: '+topic_name)
                decoded_msg = json.loads(raw_data)

                id = UUID(decoded_msg.get('to_user'))
                text = await create_message(decoded_msg)

                await insert_message(Message(id=uuid.uuid4(), text=text,user_id=id))
                await send(id, text)
                await consumer.commit()

            except json.JSONDecodeError as e:
                print(e)
            except Exception as e:
                print(e)
    finally:
        await consumer.stop()
