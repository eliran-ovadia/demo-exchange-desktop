from __future__ import annotations
from pydantic import BaseModel


class WatchlistItem(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float


class WatchlistPage(BaseModel):
    items: list[WatchlistItem]
    total: int
    page: int
    size: int
