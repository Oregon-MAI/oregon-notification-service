import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from src.data.models.message import Message
from src.repositories.message_repository import (
    delete_message_by_id,
    delete_messages_by_user_id,
    get_messages_by_user_id,
    insert_message,
)
from tests.conftest import async_iter


@pytest.mark.asyncio
async def test_get_messages_by_user_id_empty(
        mocker: MockerFixture,
        mock_redis_methods: dict[str, AsyncMock | MagicMock],
) -> None:
    user_id = uuid4()

    mock_redis_methods["scan_iter"].return_value = async_iter([])

    result = await get_messages_by_user_id(user_id)

    assert result == []
    mock_redis_methods["scan_iter"].assert_called_once_with(f"{user_id}:*")
    mock_redis_methods["mget"].assert_not_called()


@pytest.mark.asyncio
async def test_get_messages_by_user_id_with_data(
        mocker: MockerFixture,
        mock_redis_methods: dict[str, AsyncMock | MagicMock],
) -> None:
    user_id = uuid4()
    msg_id = uuid4()
    message = Message(id=msg_id, text="Test", user_id=user_id)

    mock_redis_methods["scan_iter"].return_value = async_iter([f"{user_id}:{msg_id}"])
    mock_redis_methods["mget"].return_value = [json.dumps(message.to_dict())]

    result = await get_messages_by_user_id(user_id)

    assert len(result) == 1
    assert result[0].id == msg_id
    assert result[0].text == "Test"
    mock_redis_methods["mget"].assert_called_once_with([f"{user_id}:{msg_id}"])


@pytest.mark.asyncio
async def test_insert_message(
        mocker: MockerFixture,
        mock_redis_methods: dict[str, AsyncMock | MagicMock],
) -> None:
    user_id = uuid4()
    msg_id = uuid4()
    message = Message(id=msg_id, text="New", user_id=user_id)

    await insert_message(message)

    expected_key = f"{user_id}:{msg_id}"
    mock_redis_methods["set"].assert_called_once_with(
        expected_key, json.dumps(message.to_dict())
    )


@pytest.mark.asyncio
async def test_delete_message_by_id(
        mocker: MockerFixture,
        mock_redis_methods: dict[str, AsyncMock | MagicMock],
) -> None:
    user_id = uuid4()
    msg_id = uuid4()

    await delete_message_by_id(user_id, msg_id)

    mock_redis_methods["delete"].assert_called_once_with(f"{user_id}:{msg_id}")


@pytest.mark.asyncio
async def test_delete_messages_by_user_id_empty(
        mocker: MockerFixture,
        mock_redis_methods: dict[str, AsyncMock | MagicMock],
) -> None:
    user_id = uuid4()

    mock_redis_methods["scan_iter"].return_value = async_iter([])

    await delete_messages_by_user_id(user_id)

    mock_redis_methods["scan_iter"].assert_called_once_with(f"{user_id}:*")
    mock_redis_methods["delete"].assert_not_called()


@pytest.mark.asyncio
async def test_delete_messages_by_user_id_with_keys(
        mocker: MockerFixture,
        mock_redis_methods: dict[str, AsyncMock | MagicMock],
) -> None:
    user_id = uuid4()
    keys = [f"{user_id}:msg1", f"{user_id}:msg2"]

    mock_redis_methods["scan_iter"].return_value = async_iter(keys)

    await delete_messages_by_user_id(user_id)

    mock_redis_methods["delete"].assert_called_once_with(*keys)
