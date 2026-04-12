from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.constants import DB_URL
from src.data.models.message import Message

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_messages() -> list[Message]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Message).options())
        return list(result.scalars().all())


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
