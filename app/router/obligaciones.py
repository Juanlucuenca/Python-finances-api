from cachetools import cached, TTLCache
from fastapi import APIRouter, HTTPException
from services.iol_parsing import iol_parsing, InversionType

router = APIRouter()

IOL_API_PARAM = InversionType.OBLIGACIONES.value

# Establece el caché con TTL de 800 segundos (13 minutos y 20 segundos)
cache = TTLCache(maxsize=100, ttl=800)

@router.get("/")
@cached(cache)
def get_obligaciones():
    try:
        return iol_parsing(IOL_API_PARAM)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))