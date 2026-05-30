import json
import uuid
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime
from uuid import UUID

from aiokafka import ConsumerRecord

from src.constants import MONTHS
from src.data.models.message import Message


def time_parse(iso_str: str) -> str:
    """
    Форматирует дату
    :return: строка с датой в формате "день месяц год, часы:минуты"
    """
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return f"{dt.day} {MONTHS[dt.month - 1]} {dt.year}, {dt.strftime('%H:%M')}"
    except Exception:
        return iso_str


async def create_message(
    data: ConsumerRecord,
    func: Callable[[Mapping[str, str | None]], Awaitable[Message]],
) -> Message:
    """
    Парсит сообщение из Kafka и преобразует в объект Message через переданную функцию
    :return: Message
    """
    if data.value is None:
        raise ValueError
    try:
        payload: dict[str, str | None] = json.loads(data.value.decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError
        return await func(payload)
    except Exception as e:
        raise e


async def create_user_book_message(data: Mapping[str, str | None]) -> Message:
    """
    Создаёт уведомление об успешном бронировании от имени пользователя
    :return: объект Message с текстом подтверждения
    """
    to_user = UUID(data.get("to_user"))
    status = data.get("status", "подтверждено")
    time_range = (
        f"{time_parse(str(data.get('start_time')))} - {time_parse(str(data.get('end_time')))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")

    text = f'Бронирование "{name}" ({type_}) в локации {location} успешно создано на {time_range}. Статус: {status}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_user_cancel_message(data: Mapping[str, str | None]) -> Message:
    """
    Создаёт уведомление об отмене бронирования пользователем
    :return: объект Message с текстом об отмене
    """
    to_user = UUID(data.get("to_user"))
    time_range = (
        f"{time_parse(str(data.get('start_time')))} - {time_parse(str(data.get('end_time')))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")

    text = f'Бронирование "{name}" ({type_}) в локации {location} отменено вами на {time_range}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_admin_cancel_message(data: Mapping[str, str | None]) -> Message:
    """
    Создаёт уведомление об отмене бронирования администратором
    :return: объект Message с текстом об отмене администратором
    """
    to_user = UUID(data.get("to_user"))
    status = data.get("status", "отменено")
    time_range = (
        f"{time_parse(str(data.get('start_time')))} - {time_parse(str(data.get('end_time')))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")

    text = f'Бронирование "{name}" ({type_}) в локации {location} отменено администратором на {time_range}. Статус: {status}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_admin_update_message(data: Mapping[str, str | None]) -> Message:
    """
    Создаёт уведомление об обновлении бронирования администратором
    :return: объект Message с текстом об обновлении
    """
    to_user = UUID(data.get("to_user"))
    status = data.get("status", "обновлено")
    time_range = (
        f"{time_parse(str(data.get('start_time')))} - {time_parse(str(data.get('end_time')))}"
    )
    location = data.get("location", "не указана")
    type_ = data.get("type", "услуга")
    name = data.get("name", "бронирование")
    updates = data.get("what_update", "внесены изменения")

    text = f'Бронирование "{name}" ({type_}) в локации {location} обновлено на {time_range}. Статус: {status}. Изменения: {updates}.'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_messages_message_start(data: Mapping[str, str | None]) -> Message:
    """
    Создаёт напоминание о предстоящем начале бронирования
    :return: объект Message с текстом напоминания о начале
    """
    to_user = UUID(data.get("to_user"))
    start_time = time_parse(str(data.get("start_time")))
    location = data.get("location", "не указана")
    name = data.get("name", "бронирование")

    text = f'Напоминание: бронирование "{name}" в локации {location} начнется через 15 минут (начало в {start_time}).'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_messages_message_end(data: Mapping[str, str | None]) -> Message:
    """
    Создаёт напоминание о предстоящем окончании бронирования
    :return: объект Message с текстом напоминания об окончании
    """
    to_user = UUID(data.get("to_user"))
    end_time = time_parse(str(data.get("end_time")))
    location = data.get("location", "не указана")
    name = data.get("name", "бронирование")

    text = f'Напоминание: бронирование "{name}" в локации {location} завершится через 15 минут (окончание в {end_time}).'
    return Message(id=uuid.uuid4(), text=text, user_id=to_user)


async def create_messages_message(data: Mapping[str, str | None]) -> Message:
    """
    Делегирует создание сообщения функции обработчика начала
    :return: объект Message
    """
    return await create_messages_message_start(data)
