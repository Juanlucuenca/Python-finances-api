from typing import Optional
from pydantic import BaseModel


class DolarResponse(BaseModel):
    id: str
    name: str
    buy_price: float
    sell_price: float
    update_date: Optional[str] = None

    class Config:
        from_attributes = True 