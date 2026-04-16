import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

from src.main import app


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_notifications_endpoint_returns_streaming_response(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()

    async def mock_gen() -> AsyncGenerator[str]:
        yield " Test Message\n\n"

    mocker.patch(
        "src.api.routers.notification_router.get_notifications",
        return_value=mock_gen(),
    )

    response = await async_client.get(f"/notifications/{user_id}")

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_notifications_endpoint_invalid_uuid(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/notifications/invalid-uuid")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_notifications_endpoint_service_called_with_correct_args(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()

    async def empty_gen() -> AsyncGenerator[str]:
        return
        yield

    mock_get_notifications = mocker.patch(
        "src.api.routers.notification_router.get_notifications",
        return_value=empty_gen(),
    )

    await async_client.get(f"/notifications/{user_id}")

    mock_get_notifications.assert_called_once()
    call_args = mock_get_notifications.call_args
    assert call_args[0][0] == user_id
    assert isinstance(call_args[0][1], Request)


@pytest.mark.asyncio
async def test_notifications_endpoint_multiple_events(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()

    async def mock_gen() -> AsyncGenerator[str]:
        yield " First\n\n"
        yield " Second\n\n"

    mocker.patch(
        "src.api.routers.notification_router.get_notifications",
        return_value=mock_gen(),
    )

    response = await async_client.get(f"/notifications/{user_id}")

    assert response.status_code == 200
    content = await response.aread()
    assert b" First" in content
    assert b" Second" in content
