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
from fastapi.middleware.cors import CORSMiddleware

import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # Configurar las opciones para Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Asegura que Chrome se ejecute en modo headless
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, REQUIRED on Linux
    chrome_options.add_argument("--disable-gpu")  # Aplicable para windows os only
    chrome_options.add_argument('start-maximized') # maximiza la ventana del navegador
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')

    # Iniciar el navegador en modo headless
    driver = webdriver.Chrome(options=chrome_options)

    # Ahora puedes navegar y realizar acciones como lo harías normalmente
    driver.get("https://iol.invertironline.com/mercado/cotizaciones/argentina/obligaciones-negociables/todos")
    print(driver.title)

    # Espera hasta que el elemento select esté presente en la página
    select_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "cotizaciones_length"))
    )

    # Crea un objeto Select usando el elemento encontrado
    select_obj = Select(select_element)

    # Selecciona la opción por su valor
    select_obj.select_by_value("-1")

    tabla = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "cotizaciones"))
    )

    # Extrae todas las filas de la tabla
    filas = tabla.find_elements(By.TAG_NAME, "tr")

    # Lista para almacenar los datos de cada fila
    datos_tabla = []

    # Itera sobre cada fila
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")  # o "th" si es necesario
        fila_datos = []

        for index, celda in enumerate(celdas):
            if index == 0:
                try:
                    # Intenta obtener el atributo 'data-symbol' del elemento 'a'
                    enlace = celda.find_element(By.TAG_NAME, "a")
                    simbolo = enlace.get_attribute("data-symbol")
                    fila_datos.append(simbolo)
                except NoSuchElementException:
                    # Si no hay un elemento 'a', agrega un valor predeterminado o deja la celda vacía
                    fila_datos.append("Symbol")  # o puedes usar "" para una celda vacía
            else:
                fila_datos.append(celda.text)

        datos_tabla.append(fila_datos)

    # Suponiendo que la primera fila contiene los encabezados
    encabezados = datos_tabla[0]
    datos_json = []

    # Itera sobre las filas restantes y crea un diccionario para cada una
    for fila in datos_tabla[1:]:
        fila_dict = dict(zip(encabezados, fila))
        datos_json.append(fila_dict)
        
    driver.quit()

    return datos_json