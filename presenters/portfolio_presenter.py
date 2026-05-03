from __future__ import annotations

import logging
import math
from services.api_client import api_client

logger = logging.getLogger(__name__)
from models.portfolio import PortfolioResponse

if False:
    from views.portfolio_view import PortfolioView

PAGE_SIZE = 15


class PortfolioPresenter:
    def __init__(self, view: "PortfolioView") -> None:
        self._view = view
        self._page = 1
        self._total_pages = 1

    async def load_page(self) -> None:
        logger.debug("Loading portfolio page %d", self._page)
        self._view.set_loading(True)
        try:
            data = await api_client.get_portfolio(page=self._page, page_size=PAGE_SIZE)
            resp = PortfolioResponse.model_validate(data)
            self._view.set_balance(
                account_value=resp.balance.account_value,
                buying_power=resp.balance.buying_power,
                total_return=resp.balance.total_return,
                total_return_pct=resp.balance.total_return_percent,
                total_stocks=resp.balance.total_stocks,
            )
            self._view.set_holdings([h.model_dump() for h in resp.portfolio])
            self._total_pages = max(1, math.ceil(resp.balance.total_stocks / PAGE_SIZE))
            self._view.set_page_info(self._page, self._total_pages)
            logger.debug("Portfolio page %d loaded: %d holdings", self._page, len(resp.portfolio))
        except Exception as e:
            logger.warning("Portfolio load error (page %d): %s", self._page, e)
            self._view.show_error(f"Failed to load portfolio: {e}")
            self._view.set_holdings([])
            self._view.set_page_info(1, 1)
        finally:
            self._view.set_loading(False)

    async def prev_page(self) -> None:
        if self._page > 1:
            self._page -= 1
            await self.load_page()

    async def next_page(self) -> None:
        if self._page < self._total_pages:
            self._page += 1
            await self.load_page()
