from __future__ import annotations

import httpx
from typing import Any, Awaitable, Callable
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

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
        self._refresh_hook: Callable[[], Awaitable[bool]] | None = None

    def set_token(self, token: str) -> None:
        self._access_token = token

    def clear_token(self) -> None:
        self._access_token = None

    def set_refresh_hook(self, hook: Callable[[], Awaitable[bool]]) -> None:
        """Register a coroutine that refreshes the access token. Called once on 401."""
        self._refresh_hook = hook

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
        data: dict | None = None,
        params: dict | None = None,
        auth: bool = True,
        _retry: bool = False,
    ) -> Any:
        headers = self._auth_headers() if auth else {}
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            response = await self._client.request(
                method, path, json=json, data=data, params=params, headers=headers
            )
        finally:
            QApplication.restoreOverrideCursor()

        # On 401, attempt one silent token refresh then retry
        if response.status_code == 401 and auth and not _retry and self._refresh_hook:
            refreshed = await self._refresh_hook()
            if refreshed:
                return await self._request(
                    method, path, json=json, data=data,
                    params=params, auth=auth, _retry=True,
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
            data={"username": email, "password": password},
            auth=False,
        )

    async def refresh(self, refresh_token: str) -> dict:
        return await self._request(
            "POST", "/refresh", json={"refresh_token": refresh_token}, auth=False
        )

    async def logout(self, refresh_token: str | None = None) -> None:
        # Access token goes in the Authorization header (auth=True).
        # refresh_token is optional in the body.
        body = {}
        if refresh_token:
            body["refresh_token"] = refresh_token
        await self._request("POST", "/logout", json=body, auth=True)

    # ── Users ─────────────────────────────────────────────────

    async def register(
        self,
        name: str,
        last_name: str,
        email: str,
        password: str,
        password_confirm: str,
    ) -> dict:
        return await self._request(
            "POST",
            "/api/users",
            json={
                "name": name,
                "last_name": last_name,
                "email": email,
                "password": password,
                "password_confirm": password_confirm,
            },
            auth=False,
        )

    async def reset_portfolio(self) -> dict:
        return await self._request("PATCH", "/api/portfolio/reset")

    async def delete_account(self, email: str) -> dict:
        return await self._request("DELETE", "/api/users", params={"email": email})

    # ── Portfolio ─────────────────────────────────────────────

    async def get_portfolio(self, page: int = 1, page_size: int = 50) -> dict:
        return await self._request(
            "GET", "/api/portfolio", params={"page": page, "page_size": page_size}
        )

    # ── Orders ────────────────────────────────────────────────

    async def place_order(self, symbol: str, amount: int, order_type: str) -> dict:
        return await self._request(
            "POST",
            "/api/order",
            json={"symbol": symbol, "amount": amount, "type": order_type},
        )

    # ── History ───────────────────────────────────────────────

    async def get_history(self, page: int = 1, page_size: int = 50) -> dict:
        return await self._request(
            "GET", "/api/history", params={"page": page, "page_size": page_size}
        )

    # ── Watchlist ─────────────────────────────────────────────

    async def get_watchlist(self, page: int = 1, page_size: int = 50) -> dict:
        return await self._request(
            "GET", "/api/watchlist", params={"page": page, "page_size": page_size}
        )

    async def add_to_watchlist(self, symbol: str) -> dict:
        # Stock is Depends() on the backend — symbol is a query param, not JSON body
        return await self._request("POST", "/api/watchlist", params={"symbol": symbol})

    async def remove_from_watchlist(self, symbol: str) -> dict:
        # Same: query param
        return await self._request("DELETE", "/api/watchlist", params={"symbol": symbol})

    # ── Market data ───────────────────────────────────────────

    async def get_quote(self, symbol: str) -> dict:
        # Returns dict[str, ParsedQuoteResponse] — keyed by symbol
        return await self._request("GET", "/api/quote", params={"symbol": symbol})

    async def get_market_status(self) -> dict:
        return await self._request("GET", "/api/market-status")

    async def search(self, symbol: str, page: int = 1, page_size: int = 20) -> dict:
        return await self._request(
            "GET", "/api/search", params={"symbol": symbol, "page": page, "page_size": page_size}
        )

    async def get_market_movers(self) -> dict:
        # Returns {"stocks": [{"symbol", "name", "price", "change", "percent_change"}, ...]}
        return await self._request("GET", "/api/market-movers")

    async def get_sentiment(self, symbol: str) -> dict:
        # Returns {"symbol", "strongBuy", "buy", "hold", "sell", "strongSell", "consensus"}
        return await self._request("GET", "/api/sentiment", params={"symbol": symbol})

    # ── Lifecycle ─────────────────────────────────────────────

    async def close(self) -> None:
        await self._client.aclose()


# Singleton — imported by services and presenters
api_client = APIClient()
