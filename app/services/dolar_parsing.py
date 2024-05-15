import datetime
from fastapi import HTTPException
from bs4 import BeautifulSoup
import unidecode
from utils.fetch_webpage import fetch_webpage

# Constantes
URL_DOLAR_HOY = "https://www.dolarhoy.com/"
MAX_DOLARS = 6  # Máximo de dólares a extraer

def parse_dolar_hoy():
    page_content = fetch_webpage(URL_DOLAR_HOY)
    soup = BeautifulSoup(page_content, 'lxml')
    dolars = []

    # Buscamos los bloques de dolares en la pagina
    dollars_first_six_blocks = soup.find_all('div', class_='tile is-child', limit=MAX_DOLARS)

    for dolar in dollars_first_six_blocks:
        try:
            dolars.append(parse_dolar_info(dolar)) 
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing dolar info: {e}, {dolar}")

    try:
        dolars.append(read_dolar_mayorista())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing dolar mayorista info: {e}")

    return dolars

def parse_dolar_info(dolar):
    title = dolar.find('a', class_='title').getText().strip()
    values = dolar.find('div', class_='values')
    buy = float(values.find('div', class_='compra').find('div', class_='val').get_text().strip().replace('$', ''))
    sell = float(values.find('div', class_='venta').find('div', class_='val').get_text().strip().replace('$', ''))
    dollars_id = unidecode.unidecode(title.lower().replace(" ", "_"))

    return {
        'id': dollars_id,
        'nombre': title,
        'compra': buy,
        'venta': sell,
        'fechaActualizacion': datetime.datetime.now().strftime("%d/%m, %H:%M")
    }

def read_dolar_mayorista():
    url = "https://es.investing.com/currencies/usd-ars"
    page_content = fetch_webpage(url)
    soup = BeautifulSoup(page_content, 'lxml')

    precio_dolar_mayorista = soup.find(
        'div', {'data-test': 'instrument-price-last'}).getText()

    precio_formatted = round(
        float(precio_dolar_mayorista.replace(',', '.')), 2)

    dolar_mayorista = {
        'id': 'dolar_mayorista_investing',
        'nombre': "Dolar Mayorista (investing)",
        'compra': precio_formatted,
        'venta': precio_formatted,
        'fechaActualizacion': datetime.datetime.now().strftime("%d/%m, %H:%M")
    }

    return dolar_mayorista