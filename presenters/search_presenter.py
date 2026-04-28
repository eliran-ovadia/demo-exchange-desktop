from __future__ import annotations

import asyncio
from services.api_client import api_client, APIError
from models.market import SearchResponse, ParsedQuoteResponse, SentimentEntry

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
            resp = SearchResponse.model_validate(data)
            self._view.set_results([r.model_dump() for r in resp.results])
        except APIError as e:
            self._view.show_search_error(f"Search failed: {e.detail}")
            self._view.set_results([])
        except Exception as e:
            self._view.show_search_error(f"Search failed: {e}")
            self._view.set_results([])
        finally:
            self._view.set_loading_search(False)

    async def load_detail(self, symbol: str) -> None:
        self._selected_symbol = symbol
        quote_raw, sentiment_raw = await asyncio.gather(
            api_client.get_quote(symbol),
            api_client.get_sentiment(symbol),
            return_exceptions=True,
        )

        if not isinstance(quote_raw, Exception):
            try:
                raw = quote_raw.get(symbol.upper()) or next(iter(quote_raw.values()), None)
                if raw:
                    q = ParsedQuoteResponse.model_validate(raw)
                    self._view.set_detail(
                        symbol=symbol.upper(),
                        full_name=q.full_name,
                        close=q.close,
                        change=q.change,
                        percent_change=q.percent_change,
                        open_=q.open,
                        high=q.high,
                        low=q.low,
                    )
            except Exception:
                pass

        if not isinstance(sentiment_raw, Exception):
            try:
                s = SentimentEntry.model_validate(sentiment_raw)
                self._view.set_sentiment(
                    strong_buy=s.strongBuy,
                    buy=s.buy,
                    hold=s.hold,
                    sell=s.sell,
                    strong_sell=s.strongSell,
                    consensus=s.consensus,
                )
            except Exception:
                pass

    async def add_to_watchlist(self) -> None:
        if not self._selected_symbol:
            return
        try:
            await api_client.add_to_watchlist(self._selected_symbol)
            self._view.show_watchlist_result(True, f"{self._selected_symbol} added to watchlist.")
        except APIError as e:
            self._view.show_watchlist_result(False, f"Could not add: {e.detail}")
        except Exception as e:
            self._view.show_watchlist_result(False, f"Could not add: {e}")
