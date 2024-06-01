from statistics import mean, stdev
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from db.database import get_session
from db.schemas import IndiceBigMac
from services.analysis_mac import calc_mac


router = APIRouter()

@router.get("/")
def get_mac():
    return calc_mac()

@router.post("/")
def post_mac(db: Session = Depends(get_session)):
    mac_response = calc_mac()
    nuevo_indice = IndiceBigMac()

    # Itera sobre los elementos de mac_response
    for indice in mac_response:
        # Verifica si el ID coincide con el nombre de una propiedad en IndiceBigMac
        if indice["id"] in IndiceBigMac.__fields__.keys():
            # Utiliza setattr para asignar dinámicamente el valor a la propiedad correspondiente
            setattr(nuevo_indice, indice["id"], indice["indice_mac"])
    
    db.add(nuevo_indice)
    db.commit()
    db.refresh(nuevo_indice)

    return nuevo_indice

@router.get("/analisis-mac")
def analisis_dolares(db: Session = Depends(get_session)):
    tipos_dolar = ["dolar_oficial", "dolar_blue", "dolar_bolsa",
                   "contado_con_liqui", "dolar_mayorista_sincepo"]

    resultados = {}

    for tipo in tipos_dolar:
        datos = obtener_datos_dolar(db, tipo)
        if datos:
            resultados[tipo] = {
                "promedio": mean(datos),
                "desvio_estandar": stdev(datos)
            }
        else:
            resultados[tipo] = {"promedio": None, "desvio_estandar": None}

    return resultados

def obtener_datos_dolar(db: Session, tipo_dolar: str):
    statement = select(getattr(IndiceBigMac, tipo_dolar))
    resultados = db.exec(statement).all()
    return [res for res in resultados if res is not None]

