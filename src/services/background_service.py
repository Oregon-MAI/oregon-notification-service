import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.constants import CONSUME_TOPICS
from src.consumers.consumer import cons


@asynccontextmanager
async def background(app: FastAPI) -> AsyncIterator[None]:
    print(app.version)
    tasks = [asyncio.create_task(cons(str(el))) for el in CONSUME_TOPICS]
    yield
    for task in tasks:
        task.cancel()
