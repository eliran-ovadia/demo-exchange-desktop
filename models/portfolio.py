from __future__ import annotations
from pydantic import BaseModel


class Holding(BaseModel):
    symbol: str
    name: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    gain_loss: float
    gain_loss_pct: float


class PortfolioPage(BaseModel):
    items: list[Holding]
    total: int
    page: int
    size: int
    total_value: float
    total_gain_loss: float
    total_gain_loss_pct: float
