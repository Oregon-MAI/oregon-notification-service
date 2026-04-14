import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.routers.notification_router import router as router_socket
from src.services.background_service import background

logging.basicConfig(
    level=logging.DEBUG,
    filename="notification.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

app = FastAPI(lifespan=background)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_socket)
