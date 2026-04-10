from uuid import UUID
from fastapi import Request, APIRouter
from starlette.responses import StreamingResponse
from services.connection_service import get_notifications

router = APIRouter(prefix="/notifications")

@router.get("/{user_id}")
async def notifications(user_id: UUID, request: Request):
    return StreamingResponse(get_notifications(user_id,request), media_type="text/event-stream")