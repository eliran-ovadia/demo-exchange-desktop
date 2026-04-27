from __future__ import annotations

import httpx
from typing import Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 15.0


class APIError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class APIClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)
        self._access_token: str | None = None

    def set_token(self, token: str) -> None:
        self._access_token = token

    def clear_token(self) -> None:
        self._access_token = None

    def _auth_headers(self) -> dict[str, str]:
        if self._access_token:
            return {"Authorization": f"Bearer {self._access_token}"}
        return {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict | None = None,
        auth: bool = True,
    ) -> Any:
        headers = self._auth_headers() if auth else {}
        response = await self._client.request(
            method, path, json=json, params=params, headers=headers
        )
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise APIError(response.status_code, detail)
        if response.status_code == 204:
            return None
        return response.json()

    # ── Auth ──────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> dict:
        return await self._request(
            "POST",
            "/token",
            json={"username": email, "password": password},
            auth=False,
        )

    async def refresh(self, refresh_token: str) -> dict:
        return await self._request(
            "POST", "/refresh", json={"refresh_token": refresh_token}, auth=False
        )

    async def logout(self, refresh_token: str) -> None:
        await self._request("POST", "/logout", json={"refresh_token": refresh_token})

    # ── Users ─────────────────────────────────────────────────

    async def register(self, email: str, password: str, full_name: str) -> dict:
        return await self._request(
            "POST",
            "/api/users",
            json={"email": email, "password": password, "full_name": full_name},
            auth=False,
        )

    # ── Portfolio ─────────────────────────────────────────────

    async def get_portfolio(self, page: int = 1, size: int = 50) -> dict:
        return await self._request(
            "GET", "/api/portfolio", params={"page": page, "size": size}
        )

    # ── Orders ────────────────────────────────────────────────

    async def place_order(self, symbol: str, amount: int, order_type: str) -> dict:
        return await self._request(
            "POST",
            "/api/order",
            json={"symbol": symbol, "amount": amount, "type": order_type},
        )

    # ── History ───────────────────────────────────────────────

    async def get_history(self, page: int = 1, size: int = 50) -> dict:
        return await self._request(
            "GET", "/api/history", params={"page": page, "size": size}
        )

    # ── Watchlist ─────────────────────────────────────────────

    async def get_watchlist(self, page: int = 1, size: int = 50) -> dict:
        return await self._request(
            "GET", "/api/watchlist", params={"page": page, "size": size}
        )

    async def add_to_watchlist(self, symbol: str) -> dict:
        return await self._request("POST", "/api/watchlist", json={"symbol": symbol})

    async def remove_from_watchlist(self, symbol: str) -> None:
        await self._request("DELETE", "/api/watchlist", json={"symbol": symbol})

    # ── Market data ───────────────────────────────────────────

    async def get_quote(self, symbol: str) -> dict:
        return await self._request("GET", "/api/quote", params={"symbol": symbol})

    async def get_market_status(self) -> dict:
        return await self._request("GET", "/api/market-status")

    async def search(self, symbol: str) -> dict:
        return await self._request("GET", "/api/search", params={"symbol": symbol})

    async def get_market_movers(self) -> dict:
        return await self._request("GET", "/api/market-movers")

    async def get_sentiment(self, symbol: str) -> dict:
        return await self._request(
            "GET", "/api/sentiment", params={"symbol": symbol}
        )

    # ── Lifecycle ─────────────────────────────────────────────

    async def close(self) -> None:
        await self._client.aclose()


# Singleton — imported by services and presenters
api_client = APIClient()
