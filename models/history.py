from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    symbol: str
    price: float
    amount: int
    type: str
    value: float
    profit: float
    time_stamp: datetime


class HistoryResponse(BaseModel):
    total_items: int
    page: int
    page_size: int
    history: list[Transaction]
