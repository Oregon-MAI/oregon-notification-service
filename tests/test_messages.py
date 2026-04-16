import asyncio
import uuid
from collections.abc import Generator
from typing import Any
from uuid import UUID

import pytest
from fastapi import Request
from pytest_mock import MockerFixture

from src.data.models.message import Message
from src.services.connection_service import get_notifications, send, user_messages
from src.services.messages_service import create_message


@pytest.fixture(autouse=True)
def cleanup_user_messages() -> Generator[None]:
    yield
    user_messages.clear()


@pytest.mark.asyncio
async def test_create_message_success() -> None:
    data: dict[str, Any] = {
        "status": "active",
        "start_time": "10:00",
        "end_time": "11:00",
        "location": "Office",
        "type": "Meeting",
        "name": "Sprint Planning",
        "to_user": "12345678-1234-1234-1234-123456789012",
    }
    result = await create_message(data)

    assert isinstance(result.id, UUID)
    assert "Meeting" in result.text
    assert result.user_id == UUID("12345678-1234-1234-1234-123456789012")


@pytest.mark.asyncio
async def test_create_message_default_values() -> None:
    data: dict[str, Any] = {}
    result = await create_message(data)

    assert result.text.startswith("Забронированно: , время: -")
    assert result.user_id == UUID("00000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_send_adds_message_to_queue() -> None:
    user_id = uuid.uuid4()
    message_text = "Test Notification"

    await send(user_id, message_text)

    assert user_id in user_messages
    assert len(user_messages[user_id]) == 0


@pytest.mark.asyncio
async def test_send_to_active_subscription() -> None:
    user_id = uuid.uuid4()
    message_text = "Active Sub Message"

    queue: asyncio.Queue[str] = asyncio.Queue()
    user_messages[user_id] = [queue]

    await send(user_id, message_text)

    assert not queue.empty()
    received = await queue.get()
    assert received == message_text


@pytest.mark.asyncio
async def test_get_notifications_history_yield(
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()
    mock_request = mocker.AsyncMock(spec=Request)
    mock_request.is_disconnected.return_value = True

    mock_msg = mocker.MagicMock(spec=Message)
    mock_msg.text = "History Message"

    mocker.patch(
        "src.services.connection_service.get_messages_by_user_id",
        return_value=[mock_msg],
    )
    mocker.patch(
        "src.services.connection_service.delete_messages_by_user_id",
        return_value=None,
    )

    gen = get_notifications(user_id, mock_request)
    result = await gen.__anext__()

    assert result == "data: History Message\n\n"


@pytest.mark.asyncio
async def test_get_notifications_stream_and_cleanup(
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()
    mock_request = mocker.AsyncMock(spec=Request)

    mock_request.is_disconnected.side_effect = [False, True]

    mocker.patch(
        "src.services.connection_service.get_messages_by_user_id",
        return_value=[],
    )
    mocker.patch(
        "src.services.connection_service.delete_messages_by_user_id",
        return_value=None,
    )

    async def run_gen() -> str:
        async for item in get_notifications(user_id, mock_request):
            return item
        return ""

    task = asyncio.create_task(run_gen())

    await asyncio.sleep(0.01)

    await send(user_id, "New Message")

    try:
        result = await asyncio.wait_for(task, timeout=1.0)
        assert "data: New Message" in result
    except TimeoutError:
        pytest.fail("Генератор не получил сообщение вовремя")
