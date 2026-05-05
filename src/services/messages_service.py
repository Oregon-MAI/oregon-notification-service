import json
import uuid
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime
from uuid import UUID

from aiokafka import ConsumerRecord

from src.constants import MONTHS
from src.data.models.message import Message


def parse_datetime(iso_str: str | None) -> str:
    if not iso_str or not iso_str.strip():
        return "время не указано"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return f"{dt.day} {MONTHS[dt.month - 1]} {dt.year}, {dt.strftime('%H:%M')}"
    except ValueError, IndexError:
        return iso_str


def safe_str(value: str | None, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


async def create_message(
    data: ConsumerRecord,
    func: Callable[[Mapping[str, str | None]], Awaitable[Message]],
) -> Message:
    if data.value is None:
        raise ValueError
    try:
        payload: dict[str, str | None] = json.loads(data.value.decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("Expected JSON object in Kafka payload")
        return await func(payload)
    except Exception as exc:
        raise exc


async def create_user_book_message(data: Mapping[str, str | None]) -> Message:
    to_user = UUID(data.get("to_user"))
    status = data.get("status", "подтверждено")
    time_range = (
        f"{parse_datetime(data.get('start_time'))} - {parse_datetime(data.get('end_time'))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")

    text = f'Бронирование "{name}" ({type_}) в локации {location} успешно создано на {time_range}. Статус: {status}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_user_cancel_message(data: Mapping[str, str | None]) -> Message:
    to_user = UUID(data.get("to_user"))
    time_range = (
        f"{parse_datetime(data.get('start_time'))} - {parse_datetime(data.get('end_time'))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")

    text = f'Бронирование "{name}" ({type_}) в локации {location} отменено вами на {time_range}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_admin_cancel_message(data: Mapping[str, str | None]) -> Message:
    to_user = UUID(data.get("to_user"))
    status = safe_str(data.get("status"), "отменено")
    time_range = (
        f"{parse_datetime(data.get('start_time'))} - {parse_datetime(data.get('end_time'))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")

    text = f'Бронирование "{name}" ({type_}) в локации {location} отменено администратором на {time_range}. Статус: {status}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_admin_update_message(data: Mapping[str, str | None]) -> Message:
    to_user = UUID(data.get("to_user"))
    status = safe_str(data.get("status"), "обновлено").strip()
    time_range = (
        f"{parse_datetime(data.get('start_time'))} - {parse_datetime(data.get('end_time'))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")
    updates = data.get("what_update", "внесены изменения")

    text = f'Бронирование "{name}" ({type_}) в локации {location} обновлено на {time_range}. Статус: {status}. Изменения: {updates}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_messages_message_start(data: Mapping[str, str | None]) -> Message:
    to_user = UUID(data.get("to_user"))
    start_time = parse_datetime(data.get("start_time"))
    location = data.get("location", "не указана")
    name = data.get("name", "бронирование")

    text = f'Напоминание: бронирование "{name}" в локации {location} начнется через 15 минут (начало в {start_time}).'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_messages_message_end(data: Mapping[str, str | None]) -> Message:
    to_user = UUID(data.get("to_user"))
    end_time = parse_datetime(data.get("end_time"))
    location = data.get("location", "не указана")
    name = data.get("name", "бронирование")

    text = f'Напоминание: бронирование "{name}" в локации {location} завершится через 15 минут (окончание в {end_time}).'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_messages_message(data: Mapping[str, str | None]) -> Message:
    return await create_messages_message_start(data)
