from __future__ import annotations

from services.api_client import api_client, APIError

if False:
    from views.trade_view import TradeView


class TradePresenter:
    def __init__(self, view: "TradeView") -> None:
        self._view = view
        self.current_price: float = 0.0
        self._current_symbol: str = ""

    async def load_quote(self, symbol: str) -> None:
        self._view.set_loading_quote(True)
        self._view.show_order_result(True, "")
        try:
            data = await api_client.get_quote(symbol)
            # Response is dict[symbol, ParsedQuoteResponse]
            quote = data.get(symbol.upper()) or next(iter(data.values()), None)
            if not quote:
                self._view.show_quote_error("No data returned for this symbol.")
                return
            self.current_price = quote.get("close", 0.0)
            self._current_symbol = symbol.upper()
            self._view.set_quote(
                symbol=symbol.upper(),
                full_name=quote.get("full_name", symbol),
                exchange=quote.get("exchange", ""),
                close=quote.get("close", 0.0),
                change=quote.get("change", 0.0),
                percent_change=quote.get("percent_change", 0.0),
                open_=quote.get("open", 0.0),
                high=quote.get("high", 0.0),
                low=quote.get("low", 0.0),
                volume=quote.get("volume", 0),
            )
        except APIError as e:
            self._view.show_quote_error(f"Error: {e.detail}")
        except Exception as e:
            self._view.show_quote_error(f"Could not load quote: {e}")
        finally:
            self._view.set_loading_quote(False)

    async def place_order(self) -> None:
        symbol = self._current_symbol or self._view.get_symbol()
        shares = self._view.get_shares()
        order_type = self._view.get_order_type()
        if not symbol or shares < 1:
            return
        self._view.set_loading_order(True)
        self._view.show_order_result(True, "")
        try:
            result = await api_client.place_order(symbol, shares, order_type)
            verb = "Bought" if order_type == "buy" else "Sold"
            total = result.get("value", 0.0)
            price = result.get("price", 0.0)
            self._view.show_order_result(
                True,
                f"{verb} {shares} share(s) of {symbol} @ ${price:,.2f} — Total: ${total:,.2f}"
            )
        except APIError as e:
            self._view.show_order_result(False, f"Order failed: {e.detail}")
        except Exception as e:
            self._view.show_order_result(False, f"Order failed: {e}")
        finally:
            self._view.set_loading_order(False)
