from __future__ import annotations

import math
from services.api_client import api_client
from models.history import HistoryResponse

if False:
    from views.history_view import HistoryView

PAGE_SIZE = 20


class HistoryPresenter:
    def __init__(self, view: "HistoryView") -> None:
        self._view = view
        self._page = 1
        self._total_pages = 1

    async def load_page(self) -> None:
        self._view.set_loading(True)
        try:
            data = await api_client.get_history(page=self._page, page_size=PAGE_SIZE)
            resp = HistoryResponse.model_validate(data)
            self._view.set_transactions([t.model_dump() for t in resp.history])
            self._total_pages = max(1, math.ceil(resp.total_items / PAGE_SIZE))
            self._view.set_page_info(self._page, self._total_pages)
        except Exception as e:
            self._view.show_error(f"Failed to load history: {e}")
            self._view.set_transactions([])
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
