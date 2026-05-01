import asyncio
import sys
from collections.abc import AsyncIterator, Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def async_iter(items: list[Any]) -> AsyncIterator[Any]:
    async def _iter() -> AsyncIterator[Any]:
        for item in items:
            yield item
    return _iter()


@pytest.fixture(autouse=True)
def cleanup_user_messages() -> Generator[None]:
    from src.services.connection_service import user_messages

    yield
    for queues in list(user_messages.values()):
        for q in queues:
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    break
    user_messages.clear()


@pytest.fixture
def mock_lock() -> Generator[MagicMock]:
    with patch("src.services.connection_service.lock") as mock:
        mock.__aenter__ = AsyncMock(return_value=None)
        mock.__aexit__ = AsyncMock(return_value=None)
        yield mock


@pytest.fixture
def mock_redis_methods(mocker: MockerFixture) -> dict[str, AsyncMock | MagicMock]:
    from src.repositories import message_repository

    mocks: dict[str, AsyncMock | MagicMock] = {
        "scan_iter": mocker.patch.object(
            message_repository.r, "scan_iter", new_callable=MagicMock
        ),
        "mget": mocker.patch.object(
            message_repository.r, "mget", new_callable=AsyncMock
        ),
        "set": mocker.patch.object(
            message_repository.r, "set", new_callable=AsyncMock
        ),
        "delete": mocker.patch.object(
            message_repository.r, "delete", new_callable=AsyncMock
        ),
    }
    return mocks
