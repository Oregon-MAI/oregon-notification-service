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
async def test_notifications_endpoint_streaming_response(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()

    async def mock_gen() -> AsyncGenerator[str]:
        yield "data: Test\n\n"

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
async def test_notifications_endpoint_calls_service(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()

    async def empty_gen() -> AsyncGenerator[str]:
        return
        yield  # pragma: no cover

    mock_get = mocker.patch(
        "src.api.routers.notification_router.get_notifications",
        return_value=empty_gen(),
    )

    await async_client.get(f"/notifications/{user_id}")

    mock_get.assert_called_once()
    args, _ = mock_get.call_args
    assert args[0] == user_id
    assert isinstance(args[1], Request)


@pytest.mark.asyncio
async def test_confirm_endpoint_success(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()
    message_id = uuid.uuid4()

    mock_delete = mocker.patch(
        "src.api.routers.notification_router.delete_message_by_id",
        return_value=None,
    )

    response = await async_client.post(
        f"/notifications/confirm/{user_id}/{message_id}"
    )

    assert response.status_code == 200
    # FastAPI по умолчанию сериализует str в JSON, поэтому "success" -> "\"success\""
    assert response.json() == "success"
    mock_delete.assert_called_once_with(user_id, message_id)


@pytest.mark.asyncio
async def test_confirm_endpoint_not_found(
    async_client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    user_id = uuid.uuid4()
    message_id = uuid.uuid4()

    mocker.patch(
        "src.api.routers.notification_router.delete_message_by_id",
        side_effect=Exception("Not found"),
    )

    response = await async_client.post(f"/notifications/confirm/{user_id}/{message_id}")

    assert response.status_code == 404
    assert "wrong id" in response.json()["detail"]
