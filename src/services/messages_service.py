import uuid
from uuid import UUID

from src.data.models.message import Message


async def create_message(data: dict) -> Message:
    m = Message(id=uuid.uuid4(), text="", user_id=UUID("00000000-0000-0000-0000-000000000001"))
    try:
        status = data.get("status", "")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        location = data.get("location", "")
        type = data.get("type", "")
        name = data.get("name", "")

        msg: str = f"Забронированно: {type}, время: {start_time}-{end_time}, локация: {location},  название: {name}, статус: {status}"

        m.text = msg
        m.user_id = UUID(data.get("to_user", "00000000-0000-0000-0000-000000000001"))

    except Exception as e:
        raise e

    return m
