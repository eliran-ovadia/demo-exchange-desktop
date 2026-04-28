from __future__ import annotations

import asyncio
from services.api_client import api_client, APIError
from services.auth_service import auth_service

if False:  # TYPE_CHECKING
    from views.dashboard_view import DashboardView


class DashboardPresenter:
    def __init__(self, view: "DashboardView") -> None:
        self._view = view

    async def refresh_data(self) -> None:
        self._view.show_loading(True)
        results = await asyncio.gather(
            self._fetch_portfolio(),
            self._fetch_market_status(),
            self._fetch_market_movers(),
            return_exceptions=True,
        )
        # Individual failures are surfaced per-section; don't crash the whole refresh.
        portfolio, status, movers = results

        if isinstance(portfolio, dict):
            balance = portfolio.get("balance", {})
            self._view.set_account_value(
                balance.get("account_value", 0.0),
                balance.get("total_return", 0.0),
                balance.get("total_return_percent", 0.0),
            )

        if isinstance(status, dict):
            is_open = status.get("is_open")
            exchange = status.get("exchange") or "Market"
            if is_open is None:
                label = "Status unknown"
            elif is_open:
                label = f"{exchange} Open"
            else:
                label = f"{exchange} Closed"
            self._view.set_market_status(bool(is_open), label)

        if isinstance(movers, dict):
            stocks = movers.get("stocks", [])
            gainers = sorted(
                [s for s in stocks if s.get("percent_change", 0) >= 0],
                key=lambda s: s["percent_change"],
                reverse=True,
            )
            losers = sorted(
                [s for s in stocks if s.get("percent_change", 0) < 0],
                key=lambda s: s["percent_change"],
            )
            self._view.set_movers(gainers, losers)

    async def _fetch_portfolio(self) -> dict:
        return await api_client.get_portfolio(page_size=1)

    async def _fetch_market_status(self) -> dict:
        return await api_client.get_market_status()

    async def _fetch_market_movers(self) -> dict:
        return await api_client.get_market_movers()

    async def handle_logout(self) -> None:
        await auth_service.logout()
        self._view.navigate_to_login()

    # ── Navigation stubs (filled in as each screen is built) ──

    def navigate_to_portfolio(self) -> None:
        from views.portfolio_view import PortfolioView
        self._portfolio = PortfolioView(on_back=self._view.show)
        self._portfolio.show()
        self._view.hide()

    def navigate_to_trade(self) -> None:
        from views.trade_view import TradeView
        self._trade = TradeView(on_back=self._view.show)
        self._trade.show()
        self._view.hide()

    def navigate_to_history(self) -> None:
        from views.history_view import HistoryView
        self._history = HistoryView(on_back=self._view.show)
        self._history.show()
        self._view.hide()

    def navigate_to_watchlist(self) -> None:
        from views.watchlist_view import WatchlistView
        self._watchlist = WatchlistView(on_back=self._view.show)
        self._watchlist.show()
        self._view.hide()

    def navigate_to_search(self) -> None:
        from views.search_view import SearchView
        self._search = SearchView(on_back=self._view.show)
        self._search.show()
        self._view.hide()
