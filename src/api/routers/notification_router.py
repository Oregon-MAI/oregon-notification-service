import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from starlette import status
from starlette.responses import StreamingResponse

from src.repositories.message_repository import delete_message_by_id
from src.services.connection_service import get_notifications

router = APIRouter(prefix="/notifications")


@router.get("/{user_id}")
async def notifications(user_id: UUID, request: Request) -> StreamingResponse:
    logging.info("GET: notifications user_id=%s.", user_id)
    return StreamingResponse(get_notifications(user_id, request), media_type="text/event-stream")


@router.post("/confirm/{user_id}/{message_id}")
async def confirm(user_id: UUID, message_id: UUID) -> str:
    logging.info("POST: confirm user_id=%s message_id=%s.", user_id, message_id)
    try:
        await delete_message_by_id(user_id, message_id)
        return "success"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="wrong id") from e
