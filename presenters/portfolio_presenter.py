from __future__ import annotations

import math
from services.api_client import api_client

if False:
    from views.portfolio_view import PortfolioView

PAGE_SIZE = 15


class PortfolioPresenter:
    def __init__(self, view: "PortfolioView") -> None:
        self._view = view
        self._page = 1
        self._total_pages = 1

    async def load_page(self) -> None:
        self._view.set_loading(True)
        try:
            data = await api_client.get_portfolio(page=self._page, page_size=PAGE_SIZE)
            balance = data.get("balance", {})
            self._view.set_balance(
                account_value=balance.get("account_value", 0.0),
                buying_power=balance.get("buying_power", 0.0),
                total_return=balance.get("total_return", 0.0),
                total_return_pct=balance.get("total_return_percent", 0.0),
                total_stocks=balance.get("total_stocks", 0),
            )
            self._view.set_holdings(data.get("portfolio", []))
            total_items = balance.get("total_stocks", 0)
            self._total_pages = max(1, math.ceil(total_items / PAGE_SIZE))
            self._view.set_page_info(self._page, self._total_pages)
        except Exception:
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
