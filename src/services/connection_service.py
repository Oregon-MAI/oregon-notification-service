from asyncio import Queue
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Request

from src.repositories.message_repository import get_messages_by_user_id

user_messages: dict[UUID, list[Queue]] = {}


async def send(user_id: UUID, message: str) -> None:
    if user_id not in user_messages:
        user_messages[user_id] = []
    for q in user_messages[user_id]:
        await q.put(message)


async def get_notifications(user_id: UUID, request: Request) -> AsyncGenerator[str]:
    history = await get_messages_by_user_id(user_id)
    for msg in history:
        yield "data: " + msg.text + "\n\n"

    msgs = Queue()
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(msgs)

    try:
        while True:
            if await request.is_disconnected():
                break

            msg = await msgs.get()
            yield "data: " + msg + "\n\n"

    finally:
        user_messages[user_id].remove(msgs)
