from pydantic import BaseModel
from datetime import datetime

class IndiceBigMacCreate(BaseModel):
    dolar_oficial: float
    dolar_blue: float
    dolar_bolsa: float
    dolar_liqui: float
    dolar_mayorista: float
    dolar_mayorista_sincepo: float


class IndiceBigMacRead(BaseModel):
    id: int
    fecha: datetime
    dolar_oficial: float
    dolar_bolsa: float
    dolar_blue: float
    dolar_liqui: float
    dolar_mayorista_sincepo: float

    class Config:
        from_attributes = True
