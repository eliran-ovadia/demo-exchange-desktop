from __future__ import annotations

import asyncio
from services.api_client import api_client, APIError

if False:
    from views.search_view import SearchView


class SearchPresenter:
    def __init__(self, view: "SearchView") -> None:
        self._view = view
        self._selected_symbol: str = ""

    async def search(self, query: str) -> None:
        self._view.set_loading_search(True)
        try:
            data = await api_client.search(query)
            self._view.set_results(data.get("results", []))
        except APIError as e:
            self._view.set_results([])
        except Exception:
            self._view.set_results([])
        finally:
            self._view.set_loading_search(False)

    async def load_detail(self, symbol: str) -> None:
        self._selected_symbol = symbol
        quote_data, sentiment_data = await asyncio.gather(
            api_client.get_quote(symbol),
            api_client.get_sentiment(symbol),
            return_exceptions=True,
        )

        if isinstance(quote_data, dict):
            q = quote_data.get(symbol.upper()) or next(iter(quote_data.values()), {})
            self._view.set_detail(
                symbol=symbol.upper(),
                full_name=q.get("full_name", symbol),
                close=q.get("close", 0.0),
                change=q.get("change", 0.0),
                percent_change=q.get("percent_change", 0.0),
                open_=q.get("open", 0.0),
                high=q.get("high", 0.0),
                low=q.get("low", 0.0),
            )

        if isinstance(sentiment_data, dict):
            self._view.set_sentiment(
                strong_buy=sentiment_data.get("strongBuy", 0),
                buy=sentiment_data.get("buy", 0),
                hold=sentiment_data.get("hold", 0),
                sell=sentiment_data.get("sell", 0),
                strong_sell=sentiment_data.get("strongSell", 0),
                consensus=sentiment_data.get("consensus"),
            )

    async def add_to_watchlist(self) -> None:
        if not self._selected_symbol:
            return
        try:
            await api_client.add_to_watchlist(self._selected_symbol)
        except (APIError, Exception):
            pass
