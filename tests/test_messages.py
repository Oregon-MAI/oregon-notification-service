import json
from uuid import UUID

import pytest
from aiokafka import ConsumerRecord

from src.services.messages_service import (
    create_admin_cancel_message,
    create_admin_update_message,
    create_message,
    create_messages_message,
    create_user_book_message,
    create_user_cancel_message,
)


def _make_kafka_record(value: dict | None) -> ConsumerRecord:
    return ConsumerRecord(
        topic="test",
        partition=0,
        offset=0,
        timestamp=0,
        timestamp_type=0,
        key=None,
        value=json.dumps(value).encode() if value else None,
        headers=[],
        checksum=None,
        serialized_key_size=-1,
        serialized_value_size=-1,
    )


@pytest.mark.asyncio
async def test_create_message_success() -> None:
    data = {
        "status": "active",
        "start_time": "10:00",
        "end_time": "11:00",
        "location": "Office",
        "type": "Meeting",
        "name": "Sprint",
        "to_user": "12345678-1234-1234-1234-123456789012",
    }
    record = _make_kafka_record(data)

    result = await create_message(record, create_user_book_message)

    assert isinstance(result.id, UUID)
    assert "Meeting" in result.text
    assert result.user_id == UUID("12345678-1234-1234-1234-123456789012")


@pytest.mark.asyncio
async def test_create_message_none_value_raises() -> None:
    record = _make_kafka_record(None)

    with pytest.raises(ValueError):
        await create_message(record, create_user_book_message)


@pytest.mark.asyncio
async def test_create_user_cancel_message() -> None:
    data = {
        "to_user": "11111111-1111-1111-1111-111111111111",
        "type": "Event",
        "start_time": "09:00",
        "end_time": "10:00",
        "location": "Zoom",
        "name": "Standup",
    }
    result = await create_user_cancel_message(data)

    assert result.user_id == UUID("11111111-1111-1111-1111-111111111111")
    assert "Event" in result.text
    assert "отменено вами" in result.text
    assert "Статус:" not in result.text


@pytest.mark.asyncio
async def test_create_admin_cancel_message() -> None:
    data = {
        "to_user": "22222222-2222-2222-2222-222222222222",
        "status": "cancelled",
        "type": "Booking",
        "name": "Room A",
        "start_time": "14:00",
        "end_time": "15:00",
        "location": "Building 1",
    }
    result = await create_admin_cancel_message(data)

    assert "cancelled" in result.text
    assert result.user_id == UUID("22222222-2222-2222-2222-222222222222")
    assert "отменено администратором" in result.text


@pytest.mark.asyncio
async def test_create_admin_update_message() -> None:
    data = {
        "to_user": "33333333-3333-3333-3333-333333333333",
        "what_update": "time changed",
        "type": "Meeting",
        "name": "Review",
        "start_time": "16:00",
        "end_time": "17:00",
        "location": "HQ",
        "status": "updated",
    }
    result = await create_admin_update_message(data)

    assert "time changed" in result.text
    assert "updated" in result.text
    assert "Изменения:" in result.text


@pytest.mark.asyncio
async def test_create_messages_message_with_flag() -> None:
    data = {
        "to_user": "44444444-4444-4444-4444-444444444444",
        "flag": "urgent",
        "type": "Alert",
        "name": "System",
        "start_time": "00:00",
        "end_time": "23:59",
        "location": "Cloud",
        "status": "active",
    }
    result = await create_messages_message(data)

    assert "System" in result.text
    assert "Cloud" in result.text
    assert "начнется через 15 минут" in result.text
    assert "00:00" in result.text
    assert "urgent" not in result.text
    assert "Флаг:" not in result.text


@pytest.mark.asyncio
async def test_create_messages_message_start_reminder_format() -> None:
    from src.services.messages_service import create_messages_message_start

    data = {
        "to_user": "55555555-5555-5555-5555-555555555555",
        "name": "Yoga Session",
        "location": "Studio B",
        "start_time": "2026-04-12T18:00:00Z",
    }
    result = await create_messages_message_start(data)

    assert "Yoga Session" in result.text
    assert "Studio B" in result.text
    assert "начнется через 15 минут" in result.text
    assert "12 апреля 2026, 18:00" in result.text
    assert result.user_id == UUID("55555555-5555-5555-5555-555555555555")


@pytest.mark.asyncio
async def test_create_messages_message_end_reminder_format() -> None:
    from src.services.messages_service import create_messages_message_end

    data = {
        "to_user": "66666666-6666-6666-6666-666666666666",
        "name": "Workshop",
        "location": "Main Hall",
        "end_time": "2026-04-13T20:30:00Z",
    }
    result = await create_messages_message_end(data)

    assert "Workshop" in result.text
    assert "Main Hall" in result.text
    assert "завершится через 15 минут" in result.text
    assert "13 апреля 2026, 20:30" in result.text
    assert result.user_id == UUID("66666666-6666-6666-6666-666666666666")
