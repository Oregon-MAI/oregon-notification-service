import asyncio
import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import Request
from pytest_mock import MockerFixture

from src.data.models.message import Message
from src.services.connection_service import get_notifications, send, user_messages


@pytest.mark.asyncio
async def test_send_adds_message_to_active_queues(
    mock_lock: MagicMock,
) -> None:
    user_id = uuid4()
    message = Message(id=uuid4(), text="Test", user_id=user_id)

    queue: asyncio.Queue[Message] = asyncio.Queue()
    user_messages[user_id] = [queue]

    await send(user_id, message)

    assert not queue.empty()
    received = await queue.get()
    assert received.id == message.id
    assert received.text == message.text


@pytest.mark.asyncio
async def test_send_creates_entry_for_new_user(
    mock_lock: MagicMock,
) -> None:
    user_id = uuid4()
    message = Message(id=uuid4(), text="New User", user_id=user_id)

    await send(user_id, message)

    assert user_id in user_messages
    assert user_messages[user_id] == []


@pytest.mark.asyncio
async def test_get_notifications_yields_history(
    mocker: MockerFixture,
    mock_lock: MagicMock,
) -> None:
    user_id = uuid4()
    mock_request = mocker.AsyncMock(spec=Request)
    mock_request.is_disconnected.return_value = True

    history_msg = Message(id=uuid4(), text="History", user_id=user_id)
    mocker.patch(
        "src.services.connection_service.get_messages_by_user_id",
        return_value=[history_msg],
    )

    gen = get_notifications(user_id, mock_request)
    result = await gen.__anext__()

    expected = f"data: {json.dumps(history_msg.to_dict())}\n\n"
    assert result == expected


@pytest.mark.asyncio
async def test_get_notifications_streams_live_messages(
    mocker: MockerFixture,
    mock_lock: MagicMock,
) -> None:
    user_id = uuid4()
    mock_request = mocker.AsyncMock(spec=Request)
    mock_request.is_disconnected.side_effect = [False, True]

    mocker.patch(
        "src.services.connection_service.get_messages_by_user_id",
        return_value=[],
    )

    async def run_gen() -> str:
        async for item in get_notifications(user_id, mock_request):
            return item
        return ""

    task = asyncio.create_task(run_gen())
    await asyncio.sleep(0.01)

    live_msg = Message(id=uuid4(), text="Live", user_id=user_id)
    await send(user_id, live_msg)

    result = await asyncio.wait_for(task, timeout=1.0)
    assert f"data: {json.dumps(live_msg.to_dict())}" in result


@pytest.mark.asyncio
async def test_send_respects_lock(mock_lock: MagicMock) -> None:
    user_id = uuid4()
    message = Message(id=uuid4(), text="Locked", user_id=user_id)

    await send(user_id, message)

    mock_lock.__aenter__.assert_called()
    mock_lock.__aexit__.assert_called()
