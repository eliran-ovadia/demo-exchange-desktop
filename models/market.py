from __future__ import annotations
from pydantic import BaseModel


class ParsedQuoteResponse(BaseModel):
    """Value in the dict[symbol, ParsedQuoteResponse] returned by /api/quote."""
    full_name: str
    exchange: str
    currency: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    change: float
    percent_change: float
    avg_volume: int
    year_range_high: float | None = None
    year_range_low: float | None = None


class MarketStatusResponse(BaseModel):
    exchange: str | None = None
    is_open: bool | None = None


class SearchResult(BaseModel):
    country: str
    currency: str
    exchange: str
    instrument_name: str
    symbol: str


class SearchResponse(BaseModel):
    total_results: int
    page: int
    page_size: int
    results: list[SearchResult]


class MarketMoverEntry(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    percent_change: float


class MarketMoversResponse(BaseModel):
    stocks: list[MarketMoverEntry]


class SentimentEntry(BaseModel):
    symbol: str
    strongBuy: int = 0
    buy: int = 0
    hold: int = 0
    sell: int = 0
    strongSell: int = 0
    consensus: str | None = None
