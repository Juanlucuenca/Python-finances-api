from pydantic import BaseModel


class DolarResponse(BaseModel):
    id: str
    name: str
    buy_price: float
    sell_price: float

    class Config:
        from_attributes = True 