from sqlmodel import Session, select

def getall(db: Session, entity) -> list:
    query = select(entity)
    return db.exec(query).all()