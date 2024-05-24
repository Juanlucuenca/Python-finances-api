from sqlmodel import SQLModel, Field
from datetime import datetime


class IndiceBigMac(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.now)
    dolar_oficial: float
    dolar_blue: float
    dolar_bolsa: float
    dolar_liqui: float
    dolar_mayorista_sincepo: float

class Dolares(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    compra: float
    venta: float
    fechaActualizacion: datetime = Field(default_factory=datetime.now)
