import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routers.notification_router import router as router_socket
from services.background_service import background_task
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="notification.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

@asynccontextmanager
async def background(app: FastAPI):
    task = asyncio.create_task(background_task())
    yield
    task.cancel()
    try:
        await task
    except Exception:
        print('bg cancel')


app = FastAPI(lifespan=background)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_socket)
