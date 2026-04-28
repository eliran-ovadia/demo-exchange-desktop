from __future__ import annotations
from pydantic import BaseModel


class PortfolioBalance(BaseModel):
    buying_power: float
    portfolio_value: float
    total_return: float
    total_return_percent: float
    account_value: float
    total_stocks: int


class Holding(BaseModel):
    symbol: str
    full_name: str
    amount: int
    exchange: str
    open: float
    previous_close: float
    avg_price: float
    last_price: float
    total_value: float
    bid: float
    ask: float
    year_range_low: float | None = None
    year_range_high: float | None = None
    total_return: float
    total_return_percent: float


class PortfolioResponse(BaseModel):
    balance: PortfolioBalance
    portfolio: list[Holding]
