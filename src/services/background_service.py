import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.constants import CONSUME_TOPICS
from src.consumers.consumer import cons


@asynccontextmanager
async def background(app: FastAPI) -> AsyncIterator[None]:
    print(app.version)
    tasks = [
        asyncio.create_task(cons(CONSUME_TOPICS[:2])),
        asyncio.create_task(cons(CONSUME_TOPICS[2:4])),
        asyncio.create_task(cons([CONSUME_TOPICS[4]])),
    ]
    yield
    for task in tasks:
        task.cancel()
