from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.database import get_session
from db.schemas import DolarDB
from db.repository.get_all import getall
from services.get_uva import uva_parsing

router = APIRouter()


@router.get("/dolares", response_model=List[DolarDB])
def get_dolars(db: Session = Depends(get_session)):
    try:
        return getall(db, DolarDB)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/uva")
def get_uva():
    try:
        return uva_parsing()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))