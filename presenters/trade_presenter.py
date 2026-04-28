from __future__ import annotations

from services.api_client import api_client, APIError
from models.market import ParsedQuoteResponse
from models.order import AfterOrder

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
            raw = data.get(symbol.upper()) or next(iter(data.values()), None)
            if not raw:
                self._view.show_quote_error("No data returned for this symbol.")
                return
            quote = ParsedQuoteResponse.model_validate(raw)
            self.current_price = quote.close
            self._current_symbol = symbol.upper()
            self._view.set_quote(
                symbol=symbol.upper(),
                full_name=quote.full_name,
                exchange=quote.exchange,
                close=quote.close,
                change=quote.change,
                percent_change=quote.percent_change,
                open_=quote.open,
                high=quote.high,
                low=quote.low,
                volume=quote.volume,
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
            data = await api_client.place_order(symbol, shares, order_type)
            result = AfterOrder.model_validate(data)
            verb = "Bought" if order_type == "buy" else "Sold"
            self._view.show_order_result(
                True,
                f"{verb} {shares} share(s) of {symbol} @ ${result.price:,.2f} — Total: ${result.value:,.2f}"
            )
        except APIError as e:
            self._view.show_order_result(False, f"Order failed: {e.detail}")
        except Exception as e:
            self._view.show_order_result(False, f"Order failed: {e}")
        finally:
            self._view.set_loading_order(False)
