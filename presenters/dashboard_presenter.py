from __future__ import annotations

import asyncio
import logging
from services.api_client import api_client

logger = logging.getLogger(__name__)
from models.portfolio import PortfolioResponse
from models.market import MarketStatusResponse, MarketMoversResponse

if False:
    from views.dashboard_view import DashboardView


class DashboardPresenter:
    def __init__(self, view: "DashboardView") -> None:
        self._view = view

    async def refresh_data(self) -> None:
        logger.debug("Dashboard refresh started")
        self._view.show_loading(True)
        portfolio_raw, status_raw, movers_raw = await asyncio.gather(
            api_client.get_portfolio(page_size=1),
            api_client.get_market_status(),
            api_client.get_market_movers(),
            return_exceptions=True,
        )

        if not isinstance(portfolio_raw, Exception):
            try:
                resp = PortfolioResponse.model_validate(portfolio_raw)
                self._view.set_account_value(
                    resp.balance.account_value,
                    resp.balance.total_return,
                    resp.balance.total_return_percent,
                )
            except Exception as e:
                logger.warning("Could not parse portfolio data: %s", e)
                self._view.show_error(f"Could not parse account data: {e}")
                self._view.set_account_value(0.0, 0.0, 0.0)
        else:
            logger.warning("Portfolio fetch failed: %s", portfolio_raw)
            self._view.show_error(f"Could not load account data: {portfolio_raw}")
            self._view.set_account_value(0.0, 0.0, 0.0)

        if not isinstance(status_raw, Exception):
            try:
                status = MarketStatusResponse.model_validate(status_raw)
                is_open = status.is_open
                exchange = status.exchange or "Market"
                label = f"{exchange} Open" if is_open else f"{exchange} Closed"
                if is_open is None:
                    label = "Status unknown"
                self._view.set_market_status(bool(is_open), label)
            except Exception:
                self._view.set_market_status(False, "Unavailable")
        else:
            self._view.set_market_status(False, "Unavailable")

        if not isinstance(movers_raw, Exception):
            try:
                movers = MarketMoversResponse.model_validate(movers_raw)
                gainers = sorted(
                    [s for s in movers.stocks if s.percent_change >= 0],
                    key=lambda s: s.percent_change, reverse=True,
                )
                losers = sorted(
                    [s for s in movers.stocks if s.percent_change < 0],
                    key=lambda s: s.percent_change,
                )
                self._view.set_movers(
                    [s.model_dump() for s in gainers],
                    [s.model_dump() for s in losers],
                )
            except Exception:
                self._view.set_movers([], [])
        else:
            self._view.set_movers([], [])

        logger.debug("Dashboard refresh complete")
