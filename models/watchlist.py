from pydantic import BaseModel


class WatchlistResponse(BaseModel):
    total_items: int
    page: int
    page_size: int
    watchlist: list[str]  # list of symbol strings
