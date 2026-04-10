import json
from uuid import UUID
from aiokafka import AIOKafkaConsumer
from services.connection_service import send
from constants import KAFKA_GROUP_ID, CONSUME_TOPICS, KAFKA_BOOTSTRAP_SERVERS
from services.messages_service import create_message

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
                raw_data = message.value.decode('utf-8')
                print('msg: ' + str(raw_data),'topic: '+topic_name)
                decoded_msg = json.loads(raw_data)

                id = UUID(decoded_msg.get('to_user'))
                text = await create_message(decoded_msg)
                await send(id, text)
                await consumer.commit()

            except json.JSONDecodeError as e:
                print(e)
            except Exception as e:
                print(e)
    finally:
        await consumer.stop()
