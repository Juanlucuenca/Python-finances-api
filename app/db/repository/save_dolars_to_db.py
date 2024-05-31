from typing import List
from sqlmodel import Session
from db.schemas import DolarDB


def save_dolars_to_db(dolar_list: List[DolarDB], db: Session):
    for dolar in dolar_list:
        dolar_db = DolarDB(
            id=dolar.id,
            name=dolar.name,
            buy_price=dolar.buy_price,
            sell_price=dolar.sell_price,
        )
        db.add(dolar_db)
    db.commit()