from sqlmodel import Session, select

def getall(db: Session, table) -> list:
    query = select(table)
    return db.exec(query).all()