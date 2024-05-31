from typing import Optional
from pydantic import BaseModel


class IolResponse(BaseModel):
    symbol: str
    ultimo_operado: Optional[str]
    variacion_diaria: Optional[str]
    cantidad_compra: Optional[str]
    precio_compra: Optional[str]
    precio_venta: Optional[str]
    cantidad_venta: Optional[str]
    maximo: Optional[str]
    minimo: Optional[str]
    ultimo_cierre: Optional[str]
    monto_operado: Optional[str]
    tir: Optional[str]
    duracion_md: Optional[str]

    class Config:
        from_attributes = True