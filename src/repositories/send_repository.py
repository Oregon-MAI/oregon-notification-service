from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.constants import DB_URL
from src.data.models.send import Send

engine = create_async_engine(DB_URL, echo=True, future=True)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_send(id: UUID) -> Send | None:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Send).where(Send.id == id).options())
        return result.scalar_one()


async def get_send_by_hash(hash_value: str) -> Send | None:
    async with async_session() as session:
        result = await session.execute(select(Send).where(Send.hash == hash_value))
        return result.scalar_one_or_none()


async def insert_send(new_message: Send) -> None:
    async with async_session() as session, session.begin():
        session.add(new_message)
