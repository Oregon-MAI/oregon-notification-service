import redis.asyncio as redis
from uuid import UUID
from src.constants import REDIS_PORT, REDIS_URL, REDIS_PASS
from src.data.models.message import Message
import json

r = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=0, password=REDIS_PASS, decode_responses=True)


async def get_messages_by_user_id(user_id: UUID) -> list[Message]:
    msgs = []
    keys = [key async for key in r.scan_iter(f"{user_id}:*")]
    if keys:
        for raw in await r.mget(keys):
            if raw:
                msgs.append(Message.from_dict(json.loads(raw)))
    return msgs


async def insert_message(new_message: Message) -> None:
    await r.set(f"{new_message.user_id}:{new_message.id}", json.dumps(new_message.to_dict()))


async def delete_messages_by_user_id(user_id: UUID) -> None:
    keys = [key async for key in r.scan_iter(f"{user_id}:*")]
    if keys:
        await r.delete(*keys)


"""
engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_message(id: UUID) -> Message:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Message).where(Message.id == id).options())
        return result.scalar_one()


async def get_messages_by_user_id(user_id: UUID) -> list[Message]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Message).where(Message.user_id == user_id))
        return list(result.scalars().all())


async def insert_message(new_message: Message) -> None:
    async with async_session() as session, session.begin():
        session.add(new_message)


async def delete_messages_by_user_id(user_id: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(Message).where(Message.user_id == user_id))
"""
