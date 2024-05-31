from typing import List
from sqlmodel import Session
from db.schemas import ObligacionDB


def save_obligaciones_to_db(obligaciones_list: List[ObligacionDB], db: Session):
    for obligacion in obligaciones_list:
        obligacion_db = ObligacionDB(
            symbol=obligacion.symbol,
            ultimo_operado=obligacion.ultimo_operado,
            variacion_diaria=obligacion.variacion_diaria,
            cantidad_compra=obligacion.cantidad_compra,
            precio_compra=obligacion.precio_compra,
            precio_venta=obligacion.precio_venta,
            cantidad_venta=obligacion.cantidad_venta,
            maximo=obligacion.maximo,
            minimo=obligacion.minimo,
            ultimo_cierre=obligacion.ultimo_cierre,
            monto_operado=obligacion.monto_operado,
            tir=obligacion.tir,
            duracion_md=obligacion.duracion_md
        )
        db.add(obligacion_db)
    db.commit()