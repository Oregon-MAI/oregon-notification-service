import json
import uuid
from collections.abc import Awaitable, Callable
from uuid import UUID

from aiokafka import ConsumerRecord

from src.data.models.message import Message


async def create_message(
    data: ConsumerRecord, func: Callable[[dict], Awaitable[Message]]
) -> Message:
    if data.value is None:
        raise ValueError
    try:
        d = json.loads(data.value.decode("utf-8"))
        return await func(d)
    except Exception as e:
        raise e


async def create_user_book_message(data: dict) -> Message:
    m = Message(id=uuid.uuid4(), text="", user_id=UUID("00000000-0000-0000-0000-000000000001"))
    try:
        to_user = data.get("to_user", "00000000-0000-0000-0000-000000000001")
        status = data.get("status", "")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        location = data.get("location", "")
        type = data.get("type", "")
        name = data.get("name", "")

        msg: str = f"Забронированно: {type}, время: {start_time}-{end_time}, локация: {location},  название: {name}, статус: {status}"

        m.text = msg
        m.user_id = UUID(to_user)

    except Exception as e:
        raise e

    return m


async def create_user_cancel_message(data: dict) -> Message:
    m = Message(id=uuid.uuid4(), text="", user_id=UUID("00000000-0000-0000-0000-000000000001"))
    try:
        to_user = data.get("to_user", "00000000-0000-0000-0000-000000000001")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        location = data.get("location", "")
        type = data.get("type", "")
        name = data.get("name", "")

        msg: str = f"Забронированно: {type}, время: {start_time}-{end_time}, локация: {location},  название: {name}"

        m.text = msg
        m.user_id = UUID(to_user)

    except Exception as e:
        raise e

    return m


async def create_admin_cancel_message(data: dict) -> Message:
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


async def create_admin_update_message(data: dict) -> Message:
    m = Message(id=uuid.uuid4(), text="", user_id=UUID("00000000-0000-0000-0000-000000000001"))
    try:
        status = data.get("status", "")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        location = data.get("location", "")
        type = data.get("type", "")
        name = data.get("name", "")
        updates = data.get("what_update", "")

        msg: str = f"Забронированно: {type}, время: {start_time}-{end_time}, локация: {location},  название: {name}, статус: {status}, что изменилось {updates}"

        m.text = msg
        m.user_id = UUID(data.get("to_user", "00000000-0000-0000-0000-000000000001"))

    except Exception as e:
        raise e

    return m


async def create_messages_message(data: dict) -> Message:
    m = Message(id=uuid.uuid4(), text="", user_id=UUID("00000000-0000-0000-0000-000000000001"))
    try:
        status = data.get("status", "")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        location = data.get("location", "")
        type = data.get("type", "")
        name = data.get("name", "")
        flag = data.get("flag", "")

        msg: str = f"Забронированно: {type}, время: {start_time}-{end_time}, локация: {location},  название: {name}, статус: {status}, флаг: {flag}"

        m.text = msg
        m.user_id = UUID(data.get("to_user", "00000000-0000-0000-0000-000000000001"))

    except Exception as e:
        raise e

    return m
