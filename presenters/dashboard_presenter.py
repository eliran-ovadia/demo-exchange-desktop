from __future__ import annotations

import asyncio
from services.api_client import api_client

if False:
    from views.dashboard_view import DashboardView


class DashboardPresenter:
    def __init__(self, view: "DashboardView") -> None:
        self._view = view

    async def refresh_data(self) -> None:
        self._view.show_loading(True)
        portfolio, status, movers = await asyncio.gather(
            api_client.get_portfolio(page_size=1),
            api_client.get_market_status(),
            api_client.get_market_movers(),
            return_exceptions=True,
        )

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
            label = f"{exchange} Open" if is_open else f"{exchange} Closed"
            if is_open is None:
                label = "Status unknown"
            self._view.set_market_status(bool(is_open), label)

        if isinstance(movers, dict):
            stocks = movers.get("stocks", [])
            gainers = sorted(
                [s for s in stocks if s.get("percent_change", 0) >= 0],
                key=lambda s: s["percent_change"], reverse=True,
            )
            losers = sorted(
                [s for s in stocks if s.get("percent_change", 0) < 0],
                key=lambda s: s["percent_change"],
            )
            self._view.set_movers(gainers, losers)
