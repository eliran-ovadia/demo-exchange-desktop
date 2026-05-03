from __future__ import annotations

import asyncio
import logging
from services.api_client import api_client, APIError

logger = logging.getLogger(__name__)
from models.watchlist import WatchlistResponse
from models.market import ParsedQuoteResponse

if False:
    from views.watchlist_view import WatchlistView


class WatchlistPresenter:
    def __init__(self, view: "WatchlistView") -> None:
        self._view = view

    async def load(self) -> None:
        logger.debug("Loading watchlist")
        self._view.set_loading(True)
        try:
            data = await api_client.get_watchlist(page_size=100)
            resp = WatchlistResponse.model_validate(data)
            symbols = resp.watchlist
            if not symbols:
                self._view.set_rows([])
                return
            quotes = await asyncio.gather(
                *[api_client.get_quote(s) for s in symbols],
                return_exceptions=True,
            )
            rows = []
            for symbol, quote_data in zip(symbols, quotes):
                if isinstance(quote_data, dict):
                    try:
                        raw = quote_data.get(symbol.upper()) or next(iter(quote_data.values()), {})
                        q = ParsedQuoteResponse.model_validate(raw)
                        rows.append({
                            "symbol": symbol,
                            "close": q.close,
                            "change": q.change,
                            "percent_change": q.percent_change,
                        })
                    except Exception:
                        rows.append({"symbol": symbol, "close": 0.0, "change": 0.0, "percent_change": 0.0})
                else:
                    rows.append({"symbol": symbol, "close": 0.0, "change": 0.0, "percent_change": 0.0})
            logger.debug("Watchlist loaded: %d symbols", len(rows))
            self._view.set_rows(rows)
        except Exception as e:
            logger.warning("Watchlist load error: %s", e)
            self._view.show_error(f"Failed to load watchlist: {e}")
            self._view.set_rows([])
        finally:
            self._view.set_loading(False)

    async def add_symbol(self, symbol: str) -> None:
        try:
            await api_client.add_to_watchlist(symbol)
            logger.info("Added to watchlist: %s", symbol)
            self._view.set_add_result(True, f"{symbol} added.")
            await self.load()
        except APIError as e:
            logger.warning("Watchlist add error for %s: %s", symbol, e.detail)
            self._view.set_add_result(False, e.detail)
        except Exception as e:
            logger.error("Watchlist add unexpected error for %s", symbol, exc_info=True)
            self._view.set_add_result(False, str(e))

    async def remove_selected(self) -> None:
        symbol = self._view.get_selected_symbol()
        if not symbol:
            return
        try:
            await api_client.remove_from_watchlist(symbol)
            logger.info("Removed from watchlist: %s", symbol)
            await self.load()
        except APIError as e:
            logger.warning("Watchlist remove error for %s: %s", symbol, e.detail)
            self._view.set_add_result(False, f"Remove failed: {e.detail}")
        except Exception as e:
            logger.error("Watchlist remove unexpected error for %s", symbol, exc_info=True)
            self._view.set_add_result(False, str(e))
