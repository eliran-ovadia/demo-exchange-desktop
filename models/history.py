from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    id: str
    symbol: str
    name: str
    type: str
    amount: int
    price: float
    total: float
    timestamp: datetime


class HistoryPage(BaseModel):
    items: list[Transaction]
    total: int
    page: int
    size: int
