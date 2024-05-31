import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class IndiceBigMac(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    dolar_oficial: float
    dolar_blue: float
    dolar_bolsa: float
    contado_con_liqui: float
    dolar_mayorista_sincepo: float
    entry_date: str = Field(default=datetime.datetime.now().strftime("%d/%m, %H:%M"))

class DolarDB(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, index=True)
    buy_price: float
    sell_price: float
    update_date: str = Field(default=datetime.datetime.now().strftime("%d/%m, %H:%M"))

class ObligacionDB(SQLModel, table=True):
    symbol: str = Field(default=None, primary_key=True)
    ultimo_operado: Optional[float] = Field(default=None, alias="Último Operado")
    variacion_diaria: Optional[str] = Field(default=None, alias="Variación Diaria")
    cantidad_compra: Optional[str] = Field(default=None, alias="Cantidad Compra")
    precio_compra: Optional[str] = Field(default=None, alias="Precio Compra")
    precio_venta: Optional[str] = Field(default=None, alias="Precio Venta")
    cantidad_venta: Optional[str] = Field(default=None, alias="Cantidad Venta")
    maximo: Optional[float] = Field(default=None, alias="Máximo")
    minimo: Optional[float] = Field(default=None, alias="Mínimo")
    ultimo_cierre: Optional[float] = Field(default=None, alias="Último Cierre")
    monto_operado: Optional[float] = Field(default=None, alias="Monto Operado")
    tir: Optional[str] = Field(default=None, alias="T. I. R.")
    duracion_md: Optional[int] = Field(default=None, alias="Duración (MD)")
    update_date: str = Field(default=datetime.datetime.now().strftime("%d/%m, %H:%M"))

class BonoDB(SQLModel, table=True):
    symbol: str = Field(default=None, primary_key=True)
    ultimo_operado: Optional[float] = Field(default=None, alias="Último Operado")
    variacion_diaria: Optional[str] = Field(default=None, alias="Variación Diaria")
    cantidad_compra: Optional[str] = Field(default=None, alias="Cantidad Compra")
    precio_compra: Optional[str] = Field(default=None, alias="Precio Compra")
    precio_venta: Optional[str] = Field(default=None, alias="Precio Venta")
    cantidad_venta: Optional[str] = Field(default=None, alias="Cantidad Venta")
    maximo: Optional[float] = Field(default=None, alias="Máximo")
    minimo: Optional[float] = Field(default=None, alias="Mínimo")
    ultimo_cierre: Optional[float] = Field(default=None, alias="Último Cierre")
    monto_operado: Optional[float] = Field(default=None, alias="Monto Operado")
    tir: Optional[str] = Field(default=None, alias="T. I. R.")
    duracion_md: Optional[int] = Field(default=None, alias="Duración (MD)")
    update_date: str = Field(default=datetime.datetime.now().strftime("%d/%m, %H:%M"))
