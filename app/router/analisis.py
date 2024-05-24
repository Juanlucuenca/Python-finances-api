from statistics import mean, stdev
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Dolares, IndiceBigMac
from services.calc_mac import calc_mac
from services.dolar_parsing import parse_dolar_hoy


router = APIRouter()

@router.get("/")
def get_mac():
    return calc_mac()

@router.post("/")
def post_mac(db: Session = Depends(get_session)):
    indices_mac_response = calc_mac()

    response_map = {
        # Asumiendo que este es el índice para el dólar oficial promedio
        "dolar_oficial": indices_mac_response[1]["indice_mac"],
        "dolar_blue": indices_mac_response[0]["indice_mac"],
        "dolar_bolsa": indices_mac_response[2]["indice_mac"],
        "dolar_liqui": indices_mac_response[3]["indice_mac"],
        "dolar_mayorista_investing_sincepo": indices_mac_response[4]["indice_mac"]
    }

    nuevo_indice = IndiceBigMac(
        dolar_oficial=response_map["dolar_oficial"],
        dolar_blue=response_map["dolar_blue"],
        dolar_bolsa=response_map["dolar_bolsa"],
        dolar_liqui=response_map["dolar_liqui"],
        dolar_mayorista_sincepo=response_map["dolar_mayorista_investing_sincepo"]
    )

    db.add(nuevo_indice)
    db.commit()
    db.refresh(nuevo_indice)

    return nuevo_indice

@router.get("/analisis-mac")
def analisis_dolares(db: Session = Depends(get_session)):
    tipos_dolar = ["dolar_oficial", "dolar_blue", "dolar_bolsa",
                   "dolar_liqui", "dolar_mayorista_sincepo"]

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
    # Reemplaza 'tipo_dolar' por el nombre del campo correspondiente en tu modelo
    statement = select(getattr(IndiceBigMac, tipo_dolar))
    resultados = db.exec(statement).all()
    return [res for res in resultados if res is not None]

