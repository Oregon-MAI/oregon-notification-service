import asyncio
import json
import logging
from asyncio import Queue
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Request

from src.data.models.message import Message
from src.repositories.message_repository import get_messages_by_user_id

user_messages: dict[UUID, list[Queue]] = {}

lock = asyncio.Lock()


async def send(user_id: UUID, message: Message) -> None:
    async with lock:
        if user_id not in user_messages:
            user_messages[user_id] = []
        for q in user_messages[user_id]:
            await q.put(message)
        logging.info("send: user_id=%s, message=%s.", user_id, message.to_dict())


async def get_notifications(user_id: UUID, request: Request) -> AsyncGenerator[str]:
    logging.info("get_notifications: user_id=%s.", user_id)

    msgs = Queue()
    async with lock:
        if user_id not in user_messages:
            user_messages[user_id] = []
        user_messages[user_id].append(msgs)

    history = await get_messages_by_user_id(user_id)
    for msg in history:
        yield "data: " + json.dumps(msg.to_dict()) + "\n\n"

    try:
        while True:
            if await request.is_disconnected():
                break
            msg = await msgs.get()
            yield "data: " + json.dumps(msg.to_dict()) + "\n\n"

    finally:
        async with lock:
            user_messages[user_id].remove(msgs)
