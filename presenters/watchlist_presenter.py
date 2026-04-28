from __future__ import annotations

import asyncio
from services.api_client import api_client, APIError

if False:
    from views.watchlist_view import WatchlistView


class WatchlistPresenter:
    def __init__(self, view: "WatchlistView") -> None:
        self._view = view

    async def load(self) -> None:
        self._view.set_loading(True)
        try:
            data = await api_client.get_watchlist(page_size=100)
            symbols: list[str] = data.get("watchlist", [])
            if not symbols:
                self._view.set_rows([])
                return
            # Fetch live quote for each symbol concurrently
            quotes = await asyncio.gather(
                *[api_client.get_quote(s) for s in symbols],
                return_exceptions=True,
            )
            rows = []
            for symbol, quote_data in zip(symbols, quotes):
                if isinstance(quote_data, dict):
                    q = quote_data.get(symbol.upper()) or next(iter(quote_data.values()), {})
                    rows.append({
                        "symbol": symbol,
                        "close": q.get("close", 0.0),
                        "change": q.get("change", 0.0),
                        "percent_change": q.get("percent_change", 0.0),
                    })
                else:
                    rows.append({"symbol": symbol, "close": 0.0, "change": 0.0, "percent_change": 0.0})
            self._view.set_rows(rows)
        except Exception:
            self._view.set_rows([])
        finally:
            self._view.set_loading(False)

    async def add_symbol(self, symbol: str) -> None:
        try:
            await api_client.add_to_watchlist(symbol)
            self._view.set_add_result(True, f"{symbol} added.")
            await self.load()
        except APIError as e:
            self._view.set_add_result(False, e.detail)
        except Exception as e:
            self._view.set_add_result(False, str(e))

    async def remove_selected(self) -> None:
        symbol = self._view.get_selected_symbol()
        if not symbol:
            return
        try:
            await api_client.remove_from_watchlist(symbol)
            await self.load()
        except APIError as e:
            self._view.set_add_result(False, f"Remove failed: {e.detail}")
        except Exception as e:
            self._view.set_add_result(False, str(e))
