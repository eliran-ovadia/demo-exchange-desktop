from unittest.mock import MagicMock, AsyncMock, call, patch

from presenters.trade_presenter import TradePresenter
from services.api_client import APIError

_QUOTE_RESPONSE = {
    "AAPL": {
        "full_name": "Apple Inc.",
        "exchange": "NASDAQ",
        "currency": "USD",
        "close": 150.0,
        "change": 1.5,
        "percent_change": 1.0,
        "open": 148.5,
        "high": 151.0,
        "low": 148.0,
        "volume": 50_000_000,
        "avg_volume": 55_000_000,
    }
}

_ORDER_RESPONSE = {
    "symbol": "AAPL",
    "price": 150.0,
    "amount": 5,
    "type": "buy",
    "value": 750.0,
    "profit": 0.0,
}


def make_view(symbol="AAPL", shares=5, order_type="buy"):
    view = MagicMock()
    view.get_symbol.return_value = symbol
    view.get_shares.return_value = shares
    view.get_order_type.return_value = order_type
    return view


# ── load_quote ────────────────────────────────────────────

async def test_load_quote_success_calls_set_quote():
    view = make_view()
    presenter = TradePresenter(view)
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.get_quote = AsyncMock(return_value=_QUOTE_RESPONSE)
        await presenter.load_quote("AAPL")
    view.set_quote.assert_called_once()
    assert presenter.current_price == 150.0
    assert presenter._current_symbol == "AAPL"


async def test_load_quote_success_resets_loading():
    view = make_view()
    presenter = TradePresenter(view)
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.get_quote = AsyncMock(return_value=_QUOTE_RESPONSE)
        await presenter.load_quote("AAPL")
    assert view.set_loading_quote.call_args_list == [call(True), call(False)]


async def test_load_quote_api_error_shows_error():
    view = make_view()
    presenter = TradePresenter(view)
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.get_quote = AsyncMock(side_effect=APIError(404, "Symbol not found"))
        await presenter.load_quote("AAPL")
    view.show_quote_error.assert_called_once_with("Error: Symbol not found")
    view.set_quote.assert_not_called()


async def test_load_quote_empty_response_shows_error():
    view = make_view()
    presenter = TradePresenter(view)
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.get_quote = AsyncMock(return_value={})
        await presenter.load_quote("AAPL")
    view.show_quote_error.assert_called_once_with("No data returned for this symbol.")


async def test_load_quote_loading_always_reset_on_error():
    view = make_view()
    presenter = TradePresenter(view)
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.get_quote = AsyncMock(side_effect=APIError(500, "Server error"))
        await presenter.load_quote("AAPL")
    assert view.set_loading_quote.call_args_list == [call(True), call(False)]


# ── place_order ───────────────────────────────────────────

async def test_place_order_success_shows_confirmation():
    view = make_view()
    presenter = TradePresenter(view)
    presenter._current_symbol = "AAPL"
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.place_order = AsyncMock(return_value=_ORDER_RESPONSE)
        await presenter.place_order()
    view.show_order_result.assert_called_with(
        True, "Bought 5 share(s) of AAPL @ $150.00 — Total: $750.00"
    )


async def test_place_order_sell_shows_sold_verb():
    view = make_view(order_type="sell")
    presenter = TradePresenter(view)
    presenter._current_symbol = "AAPL"
    response = {**_ORDER_RESPONSE, "type": "sell"}
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.place_order = AsyncMock(return_value=response)
        await presenter.place_order()
    args = view.show_order_result.call_args[0]
    assert args[0] is True
    assert "Sold" in args[1]


async def test_place_order_no_symbol_skips_api_call():
    view = make_view(symbol="")
    presenter = TradePresenter(view)
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.place_order = AsyncMock()
        await presenter.place_order()
    mock_client.place_order.assert_not_called()


async def test_place_order_zero_shares_skips_api_call():
    view = make_view(shares=0)
    presenter = TradePresenter(view)
    presenter._current_symbol = "AAPL"
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.place_order = AsyncMock()
        await presenter.place_order()
    mock_client.place_order.assert_not_called()


async def test_place_order_api_error_shows_failure():
    view = make_view()
    presenter = TradePresenter(view)
    presenter._current_symbol = "AAPL"
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.place_order = AsyncMock(side_effect=APIError(400, "Insufficient funds"))
        await presenter.place_order()
    view.show_order_result.assert_called_with(False, "Order failed: Insufficient funds")


async def test_place_order_loading_always_reset():
    view = make_view()
    presenter = TradePresenter(view)
    presenter._current_symbol = "AAPL"
    with patch("presenters.trade_presenter.api_client") as mock_client:
        mock_client.place_order = AsyncMock(side_effect=APIError(400, "Insufficient funds"))
        await presenter.place_order()
    assert view.set_loading_order.call_args_list == [call(True), call(False)]
