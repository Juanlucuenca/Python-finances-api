from fastapi import APIRouter, HTTPException
from services.dolar_parsing import parse_dolar_hoy
from services.uva_parsing import uva_parsing

router = APIRouter()


@router.get("/dolares")
def get_dolars():
    try:
        return parse_dolar_hoy()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/uva")
def get_uva():
    try:
        return uva_parsing()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))