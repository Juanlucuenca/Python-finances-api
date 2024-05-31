from typing import List
from sqlmodel import Session
from db.schemas import BonoDB


def save_bonos_to_db(Bono_list: List[BonoDB], db: Session):
    for bono in Bono_list:
        bono_db = BonoDB(
            symbol=bono.symbol,
            ultimo_operado=bono.ultimo_operado,
            variacion_diaria=bono.variacion_diaria,
            cantidad_compra=bono.cantidad_compra,
            precio_compra=bono.precio_compra,
            precio_venta=bono.precio_venta,
            cantidad_venta=bono.cantidad_venta,
            maximo=bono.maximo,
            minimo=bono.minimo,
            ultimo_cierre=bono.ultimo_cierre,
            monto_operado=bono.monto_operado,
            tir=bono.tir,
            duracion_md=bono.duracion_md
        )
        db.add(bono_db)
    db.commit()