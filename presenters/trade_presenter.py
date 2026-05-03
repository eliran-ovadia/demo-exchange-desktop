from __future__ import annotations

import logging
from services.api_client import api_client, APIError

logger = logging.getLogger(__name__)
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
        logger.debug("Loading quote: %s", symbol)
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
            logger.debug("Quote loaded: %s @ $%.2f", symbol.upper(), quote.close)
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
            logger.warning("Quote error for %s: %s", symbol, e.detail)
            self._view.show_quote_error(f"Error: {e.detail}")
        except Exception as e:
            logger.error("Quote unexpected error for %s", symbol, exc_info=True)
            self._view.show_quote_error(f"Could not load quote: {e}")
        finally:
            self._view.set_loading_quote(False)

    async def place_order(self) -> None:
        symbol = self._current_symbol or self._view.get_symbol()
        shares = self._view.get_shares()
        order_type = self._view.get_order_type()
        if not symbol or shares < 1:
            return
        logger.debug("Placing %s order: %d x %s", order_type, shares, symbol)
        self._view.set_loading_order(True)
        self._view.show_order_result(True, "")
        try:
            data = await api_client.place_order(symbol, shares, order_type)
            result = AfterOrder.model_validate(data)
            logger.info("Order placed: %s %d %s @ $%.2f", order_type, shares, symbol, result.price)
            verb = "Bought" if order_type == "buy" else "Sold"
            self._view.show_order_result(
                True,
                f"{verb} {shares} share(s) of {symbol} @ ${result.price:,.2f} — Total: ${result.value:,.2f}"
            )
        except APIError as e:
            logger.warning("Order failed for %s: %s", symbol, e.detail)
            self._view.show_order_result(False, f"Order failed: {e.detail}")
        except Exception as e:
            logger.error("Order unexpected error for %s", symbol, exc_info=True)
            self._view.show_order_result(False, f"Order failed: {e}")
        finally:
            self._view.set_loading_order(False)
