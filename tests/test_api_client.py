from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from services.api_client import APIClient, APIError


@pytest.fixture
def client():
    """Fresh APIClient with Qt cursor calls patched out."""
    with patch("services.api_client.QApplication"):
        yield APIClient()


def mock_request(*responses):
    """Return an AsyncMock that yields each httpx.Response in order."""
    mock = AsyncMock(side_effect=list(responses))
    return mock


# ── Happy path ────────────────────────────────────────────

async def test_successful_request_returns_json(client):
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(
            httpx.Response(200, json={"result": "ok"})
        )
        result = await client._request("GET", "/test")
    assert result == {"result": "ok"}


async def test_204_returns_none(client):
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(httpx.Response(204))
        result = await client._request("GET", "/test")
    assert result is None


# ── HTTP errors ───────────────────────────────────────────

async def test_4xx_raises_api_error(client):
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(
            httpx.Response(400, json={"detail": "Bad request"})
        )
        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "/test")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Bad request"


async def test_5xx_raises_api_error(client):
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(
            httpx.Response(500, json={"detail": "Server error"})
        )
        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "/test")
    assert exc_info.value.status_code == 500


# ── 401 refresh retry ─────────────────────────────────────

async def test_401_with_refresh_hook_retries_and_succeeds(client):
    refresh_hook = AsyncMock(return_value=True)
    client.set_refresh_hook(refresh_hook)
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(
            httpx.Response(401),
            httpx.Response(200, json={"result": "ok"}),
        )
        result = await client._request("GET", "/test")
    refresh_hook.assert_awaited_once()
    assert result == {"result": "ok"}


async def test_401_without_refresh_hook_raises_api_error(client):
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(httpx.Response(401))
        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "/test")
    assert exc_info.value.status_code == 401


async def test_401_refresh_fails_raises_api_error(client):
    refresh_hook = AsyncMock(return_value=False)
    client.set_refresh_hook(refresh_hook)
    with patch("services.api_client.QApplication"):
        client._client.request = mock_request(
            httpx.Response(401),
            httpx.Response(401),
        )
        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "/test")
    assert exc_info.value.status_code == 401


# ── Network errors ────────────────────────────────────────

async def test_transport_error_raises_friendly_api_error(client):
    with patch("services.api_client.QApplication"):
        client._client.request = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "/test")
    assert exc_info.value.status_code == 0
    assert "Could not reach server" in exc_info.value.detail


async def test_timeout_raises_friendly_api_error(client):
    with patch("services.api_client.QApplication"):
        client._client.request = AsyncMock(
            side_effect=httpx.ReadTimeout("Timed out")
        )
        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "/test")
    assert exc_info.value.status_code == 0
