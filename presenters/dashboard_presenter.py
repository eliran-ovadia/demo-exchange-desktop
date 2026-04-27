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
            self._view.set_account_value(
                portfolio.get("total_value", 0.0),
                portfolio.get("total_gain_loss", 0.0),
                portfolio.get("total_gain_loss_pct", 0.0),
            )

        if isinstance(status, dict):
            self._view.set_market_status(
                status.get("is_open", False),
                status.get("message", "Unknown"),
            )

        if isinstance(movers, dict):
            self._view.set_movers(
                movers.get("gainers", []),
                movers.get("losers", []),
            )

    async def _fetch_portfolio(self) -> dict:
        return await api_client.get_portfolio(size=1)

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
