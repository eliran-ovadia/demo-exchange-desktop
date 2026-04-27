from pydantic import BaseModel


class OrderResult(BaseModel):
    order_id: str
    symbol: str
    amount: int
    type: str
    price: float
    total: float
    status: str
