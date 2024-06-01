from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session
from models.IolResponse import IolResponse
from db.schemas import BonoDB
from db.database import get_session
from db.repository.get_all import getall

router = APIRouter()

@router.get("/", response_model=List[IolResponse])
def get_bonos(db: Session = Depends(get_session)):
    try:
        return getall(db, BonoDB)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))