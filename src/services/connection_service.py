import asyncio
from uuid import UUID

user_messages: dict[UUID, asyncio.Queue] = {}

async def get_queue(user_id: UUID) -> asyncio.Queue:
    if user_id not in user_messages:
        user_messages[user_id] = asyncio.Queue()
    return user_messages[user_id]

async def send(user_id: UUID, message: str):
    if user_id not in user_messages:
        user_messages[user_id] = asyncio.Queue()
    await user_messages[user_id].put(message)


async def get_notifications(user_id, request):
    queue = await get_queue(user_id)
    try:
        while True:
            if await request.is_disconnected():
                break
            data = await queue.get()
            yield "data: "+str(data)+"\n\n"
    finally:
        print('close')
