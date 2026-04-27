from __future__ import annotations
from pydantic import BaseModel


class Quote(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    volume: int
    market_cap: float | None = None
    pe_ratio: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None


class MarketStatus(BaseModel):
    is_open: bool
    message: str


class SearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str | None = None
    type: str | None = None


class Mover(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float


class MarketMovers(BaseModel):
    gainers: list[Mover]
    losers: list[Mover]


class Sentiment(BaseModel):
    symbol: str
    consensus: str
    buy: int
    hold: int
    sell: int
    target_price: float | None = None
