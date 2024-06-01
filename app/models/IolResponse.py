from typing import Optional
from pydantic import BaseModel


class IolResponse(BaseModel):
    symbol: str
    ultimo_operado: Optional[float]
    variacion_diaria: Optional[str]
    cantidad_compra: Optional[str]
    precio_compra: Optional[str]
    precio_venta: Optional[str]
    cantidad_venta: Optional[str]
    maximo: Optional[float]
    minimo: Optional[float]
    ultimo_cierre: Optional[float]
    monto_operado: Optional[float]
    tir: Optional[str]
    duracion_md: Optional[float]

    class Config:
        from_attributes = True