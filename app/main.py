from statistics import mean, stdev
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from unidecode import unidecode
from schemas import IndiceBigMacCreate
from models import IndiceBigMac
from database import create_db_and_tables, get_session

app = FastAPI()

# Inicializa la base de datos (si es necesario)


@app.on_event("startup")
async def startup_event():
    create_db_and_tables()


@app.get("/dolarMayorista")
def read_dolar_mayorista():
    # Formateamos la fecha actual
    formated_datetime = datetime.datetime.now().strftime("%d/%m, %H:%M")


    # Solicitamos la pagina y la parseamos
    website_content = requests.get(
        "https://es.investing.com/currencies/usd-ars").text

    soup = BeautifulSoup(website_content, 'lxml')

    precio_dolar_mayorista = soup.find(
        'div', {'data-test': 'instrument-price-last'}).getText()

    precio_formatted = round(float(precio_dolar_mayorista.replace(',', '.')), 2)

    dolar_mayorista = {
        'id': 'dolar_mayorista_investing',
        'nombre': "Dolar Mayorista (investing)",
        'compra': precio_formatted,
        'venta': precio_formatted,
        'fechaActualizacion': 'Fecha de actualización: ' + formated_datetime
    }

    return dolar_mayorista


@app.get("/dolares")
def read_dolars():

    # Formateamos la fecha actual
    formated_datetime = datetime.datetime.now().strftime("%d/%m, %H:%M")

    # Solicitamos la pagina y la parseamos
    website_content = requests.get("https://www.dolarhoy.com/").text
    soup = BeautifulSoup(website_content, 'lxml')

    # Buscamos lo importante de la pagina
    bloque_dolares = soup.find_all('div', class_='tile is-child')

    # Obtener los primeros 6 elementos - Otros Dolares de importancia
    primeros_seis = bloque_dolares[:5]

    # Creamos una lista vacia para guardar los dolares
    dolar_list = []

    for dolar in primeros_seis:

        try:
            title = dolar.find('a', class_='title').getText().strip()
            # Obtenemos el div con los valores de venta y compra
            values = dolar.find('div', class_='values')

            # Obtenemos el precio del dolar - (compra)
            buy = float(values.find('div', class_='compra').find(
                'div', class_='val').get_text().strip().replace('$', ''))

            # Obtenemos el precio del dolar - (venta)
            sell = float(values.find('div', class_='venta').find(
                'div', class_='val').get_text().strip().replace('$', ''))

            # Obtener el nombre en minúsculas y sin tildes
            dollars_id = unidecode((title).lower().replace(" ", "_"))

            # Crear un diccionario con la información y agregarlo a la lista
            dolar = {
                'id': dollars_id,
                'nombre': title,
                'compra': buy,
                'venta': sell,
                'fechaActualizacion': 'Fecha de actualización: ' + formated_datetime
            }
        except Exception as e:
            continue

        dolar_list.append(dolar)

    for bloque in bloque_dolares:
        try:
            title = bloque.find('div', class_='title').getText().strip()
        except Exception as e:
            continue

        if title and 'Dólar Mayorista' in title:
            buy = float(bloque.find('div', class_='compra').getText(
            ).strip().replace('$', ''))
            sell = float(bloque.find('div', class_='venta').getText(
            ).strip().replace('$', ''))
            dollars_id = unidecode((title).lower().replace(" ", "_"))

            dolar = {
                'id': dollars_id + "_dolarhoy",
                'nombre': title + "(DolarHoy)",
                'compra': buy,
                'venta': sell,
                'fechaActualizacion': 'Fecha de actualización: ' + formated_datetime
            }

            dolar_list.append(dolar)
            break

    dolar_mayorista_investing = read_dolar_mayorista()

    dolar_list.append(dolar_mayorista_investing)

    return dolar_list


@app.get("/uva")
def read_uva():
    preciosUva = requests.get(
        "https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/")

    if (preciosUva.status_code != 200):
        return "Error al obtener los datos de la API"

    datos = preciosUva.json()

    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

    uva_actual = next(
        (item for item in datos if item["fecha"] == fecha_actual), None)

    if uva_actual:
        return uva_actual
    else:
        return HTTPException("No se encontró una uva para la fecha actual.")


@app.get("/mac")
def calc_mac():
    mac_list = []

    uva = read_uva()
    dolares = read_dolars()

    for dolar in dolares:
        dollar_id = dolar['id']
        name = dolar['nombre']
        sell_price = dolar['venta']

        if (dollar_id == 'dolar_oficial'):
            indice_mac = (3.5 * 742.0 * uva['valor'] /
                          386.91) / sell_price

        elif (dollar_id == 'dolar_blue' or dollar_id == 'dolar_bolsa' or dollar_id == 'contado_con_liqui'):
            indice_mac = (2.25 * 1155.0 * uva['valor'] /
                          386.91) / sell_price

        elif (dollar_id == 'dolar_mayorista_investing'):
            indice_mac = (3.345*777.0*uva['valor'] / 386.91) / sell_price
            dollar_id = dollar_id + '_sincepo'
            name = name + ' (SINCEPO)'

            mac_list.append({
                'id': dollar_id,
                'nombre': name,
                'indice_mac': indice_mac
            })

            dollar_id = dolar['id']
            name = dolar['nombre']

            indice_mac = (3.5 * 742.0 * uva['valor'] /
                          386.91) / sell_price
        else:
            continue

        mac_list.append({
            'id': dollar_id,
            'nombre': name,
            'indice_mac': indice_mac
        })

    return mac_list


@app.post('/mac')
def create_mac(db: Session = Depends(get_session)):
    indices_mac_response = calc_mac()

    response_map = {
        # Asumiendo que este es el índice para el dólar oficial promedio
        "dolar_oficial": indices_mac_response[1]["indice_mac"],
        "dolar_blue": indices_mac_response[0]["indice_mac"],
        "dolar_bolsa": indices_mac_response[2]["indice_mac"],
        "dolar_liqui": indices_mac_response[3]["indice_mac"],
        "dolar_mayorista_investing": indices_mac_response[5]["indice_mac"],
        "dolar_mayorista_investing_sincepo": indices_mac_response[4]["indice_mac"]
    }

    nuevo_indice = IndiceBigMac(
        dolar_oficial=response_map["dolar_oficial"],
        dolar_blue=response_map["dolar_blue"],
        dolar_bolsa=response_map["dolar_bolsa"],
        dolar_liqui=response_map["dolar_liqui"],
        dolar_mayorista=response_map["dolar_mayorista_investing"],
        dolar_mayorista_sincepo=response_map["dolar_mayorista_investing_sincepo"]
    )

    db.add(nuevo_indice)
    db.commit()
    db.refresh(nuevo_indice)

    return nuevo_indice


def obtener_datos_dolar(db: Session, tipo_dolar: str):
    # Reemplaza 'tipo_dolar' por el nombre del campo correspondiente en tu modelo
    statement = select(getattr(IndiceBigMac, tipo_dolar))
    resultados = db.exec(statement).all()
    return [res for res in resultados if res is not None]


@app.get("/analisis-mac")
def analisis_dolares(db: Session = Depends(get_session)):
    tipos_dolar = ["dolar_oficial", "dolar_blue", "dolar_bolsa",
                   "dolar_liqui", "dolar_mayorista", "dolar_mayorista_sincepo"]

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
@app.get('/obligaciones')
def get_obligaciones():
    # URL and headers based on the provided cURL command
    url = 'https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/negociable-obligations'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'JSESSIONID=B66C6B881A9D68B218F0207EBAFFC0C3; _fbp=fb.2.1705410945340.696063700; _gid=GA1.3.557642713.1705410949; _ga=GA1.1.396957812.1705410949; _ga_7RDWSKPMBV=GS1.1.1705425982.2.1.1705428062.60.0.0',
        'Origin': 'https://open.bymadata.com.ar',
        'Referer': 'https://open.bymadata.com.ar/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    # Data to be sent in request body
    data = {
        "excludeZeroPxAndQty": True,
        "T2": True,
        "T1": False,
        "T0": False,
        "Content-Type": "application/json"
    }

    # Enviando solicitud POST
    response = requests.post(url, json=data, headers=headers)
    list_of_data = response.json()  # Esto es una lista de objetos

    # Inicializamos una lista para los datos mapeados
    mapped_data_list = []

    # Iteramos sobre cada objeto en la lista
    for data in list_of_data:
        # Mapeo de los datos recibidos a los nombres de la tabla
        mapped_data = {
            "Especie": data.get("symbol", ""),
            "Vto.": data.get("maturityDate", ""),
            "Moneda": data.get("denominationCcy", ""),
            "C. Cpra.": data.get("quantityBid", 0),
            "P. Cpra.": data.get("bidPrice", 0.0),
            "P. Vta.": data.get("offerPrice", 0.0),
            "C. Vta.": data.get("quantityOffer", 0),
            "Apertura": data.get("openingPrice", 0.0),
            "Mínimo": data.get("tradingLowPrice", 0.0),
            "Máximo": data.get("tradingHighPrice", 0.0),
            "Último": data.get("trade", 0.0),
            "Cierre Ant.": data.get("previousClosingPrice", 0.0),
            "Cierre": data.get("closingPrice", 0.0),
            "Dir.": "↑" if data.get("tickDirection", 0) > 0 else "↓" if data.get("tickDirection", 0) < 0 else "→",
            "Var.": data.get("imbalance", 0.0),
            "Volumen": data.get("volume", 0),
            "Vol. Monto": data.get("volumeAmount", 0.0),
            "Vwap": data.get("vwap", 0.0),
            "Hora": data.get("tradeHour", "")
        }
        mapped_data_list.append(mapped_data)

    # Devolver la lista de datos mapeados
    return mapped_data_list