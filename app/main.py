from statistics import mean, stdev
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from unidecode import unidecode
from schemas import IndiceBigMacCreate
from models import Dolares, IndiceBigMac
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


@app.post('/dolares')
def guardar_dolares(db: Session = Depends(get_session)):
    cotizaciones_dolares = read_dolars()

    for cotizacion_dolar in cotizaciones_dolares:
        cotizacion_map = Dolares(
            nombre=cotizacion_dolar["id"],
            compra=cotizacion_dolar["compra"],
            venta=cotizacion_dolar["venta"],
            fechaActualizacion=cotizacion_dolar["fechaActualizacion"]
        )
        db.add(cotizacion_map)

    db.commit()


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
    # Asegura que Chrome se ejecute en modo headless
    chrome_options.add_argument("--headless")
    # Bypass OS security model, REQUIRED on Linux
    chrome_options.add_argument("--no-sandbox")
    # Aplicable para windows os only
    chrome_options.add_argument("--disable-gpu")
    # maximiza la ventana del navegador
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--disable-web-security")

    # Iniciar el navegador en modo headless
    driver = webdriver.Chrome(options=chrome_options)

    # Ahora puedes navegar y realizar acciones como lo harías normalmente
    driver.get(
        "https://iol.invertironline.com/mercado/cotizaciones/argentina/obligaciones-negociables/todos")
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

    datos_tabla = []
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        fila_datos = []

        for index, celda in enumerate(celdas):
            if index == 0:
                try:
                    enlace = celda.find_element(By.TAG_NAME, "a")
                    simbolo = enlace.get_attribute("data-symbol")
                    fila_datos.append(simbolo)
                except NoSuchElementException:
                    fila_datos.append("Symbol")
            else:
                # Usa la función convertir_valor_numerico para ajustar los valores numéricos
                valor_ajustado = convertir_valor_numerico(celda.text)
                fila_datos.append(valor_ajustado)

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


def convertir_valor_numerico(valor):
    # Intenta convertir valores numéricos al formato correcto (punto decimal)
    try:
        # Primero, verifica si el valor contiene comas que puedan indicar decimales
        if "," in valor:
            # Elimina puntos que puedan ser separadores de miles
            valor_sin_puntos = valor.replace(".", "")
            # Luego, reemplaza la coma por un punto para el decimal
            return valor_sin_puntos.replace(",", ".")
        else:
            # Devuelve el valor original si no necesita conversión
            return valor
    except ValueError:
        # Devuelve el valor original si ocurre un error en la conversión
        return valor


@app.get('/bonos')
def get_obligaciones():
    # Configurar las opciones para Chrome en modo headless
    chrome_options = Options()
    # Asegura que Chrome se ejecute en modo headless
    chrome_options.add_argument("--headless")
    # Bypass OS security model, REQUIRED on Linux
    chrome_options.add_argument("--no-sandbox")
    # Aplicable para windows os only
    chrome_options.add_argument("--disable-gpu")
    # maximiza la ventana del navegador
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--disable-web-security")

    # Iniciar el navegador en modo headless
    driver = webdriver.Chrome(options=chrome_options)

    # Ahora puedes navegar y realizar acciones como lo harías normalmente
    driver.get(
        "https://iol.invertironline.com/mercado/cotizaciones/argentina/bonos/todos")
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

    datos_tabla = []
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        fila_datos = []

        for index, celda in enumerate(celdas):
            if index == 0:
                try:
                    enlace = celda.find_element(By.TAG_NAME, "a")
                    simbolo = enlace.get_attribute("data-symbol")
                    fila_datos.append(simbolo)
                except NoSuchElementException:
                    fila_datos.append("Symbol")
            else:
                # Usa la función convertir_valor_numerico para ajustar los valores numéricos
                valor_ajustado = convertir_valor_numerico(celda.text)
                fila_datos.append(valor_ajustado)

        datos_tabla.append(fila_datos)

    # Suponiendo que la primera fila contiene los encabezados
    encabezados = datos_tabla[0]
    datos_json = []

    # Itera sobre las filas restantes y crea un diccionario para cada una
    for fila in datos_tabla[1:]:
        fila_dict = dict(zip(encabezados, fila))
        datos_json.append(fila_dict)

    driver.quit()

    #ordenar por el symbol esta lista de obligaciones datos_json
    datos_json.sort(key=lambda x: x['Symbol'])

    return datos_json
