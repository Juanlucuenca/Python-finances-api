from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.database import get_session
from db.repository.get_all import getall
from db.schemas import ObligacionDB

router = APIRouter()

@router.get("/", response_model=List[ObligacionDB])
def get_obligaciones(db: Session = Depends(get_session)):
    try:
        return getall(db, ObligacionDB)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))