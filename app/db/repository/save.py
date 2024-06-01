from typing import List
from sqlmodel import SQLModel, Session


def save(entity_list: List[SQLModel], db: Session, model):
    for entity in entity_list:
        try:
            db_entity = model(**entity.model_dump())
            db.add(db_entity)
            print(f"Saved {entity} to db")
        except Exception as e:
            print(f"Error saving bono {entity} to db: {e}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error saving bonos to db: {e}")