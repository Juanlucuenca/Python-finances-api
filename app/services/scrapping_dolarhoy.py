import datetime
import traceback

from typing import List
from fastapi import HTTPException
from bs4 import BeautifulSoup
import unidecode

from utils.fetch_webpage import fetch_webpage
from models.DolarResponse import DolarResponse

def scrapping_dolarhoy() -> List[DolarResponse]:
    page_content = fetch_webpage("https://www.dolarhoy.com/")
    soup = BeautifulSoup(page_content, 'lxml')
    dolars_list: List[DolarResponse] = []

    dollars_html_list = soup.find_all('div', class_='tile is-child', limit=5)

    for dolar_html in dollars_html_list:
        dolars_list.append(parse_dolar_info(dolar_html)) 
        
    dolar_mayorista_html = soup.find('div', class_='title', text=lambda t: t and 'Dólar Mayorista' in t).parent.parent
    dolars_list.append(parse_dolar_mayorista(dolar_mayorista_html))

    return dolars_list


def parse_dolar_mayorista(dolar_mayorista_html: BeautifulSoup) -> DolarResponse:
    try:
        title = dolar_mayorista_html.find('div', class_='title').getText().strip()
        buy = float(dolar_mayorista_html.find('div', class_='compra').getText(
                ).strip().replace('$', ''))
        sell = float(dolar_mayorista_html.find('div', class_='venta').getText(
                ).strip().replace('$', ''))
        dollars_id = unidecode.unidecode((title).lower().replace(" ", "_"))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing dolar mayorista info: {e}")

    return DolarResponse(
        id=dollars_id,
        name=title,
        buy_price=buy,
        sell_price=sell,
    )

def parse_dolar_info(dolar_html: BeautifulSoup) -> DolarResponse:
    try:
        title = dolar_html.find('a', class_='title').getText().strip()
        values = dolar_html.find('div', class_='values')
        buy = float(values.find('div', class_='compra').find('div', class_='val').get_text().strip().replace('$', ''))
        sell = float(values.find('div', class_='venta').find('div', class_='val').get_text().strip().replace('$', ''))
        dollars_id = unidecode.unidecode(title.lower().replace(" ", "_"))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing dolar info of {dolar_html}: {e}")

    return DolarResponse(
        id=dollars_id,
        name=title,
        buy_price=buy,
        sell_price=sell,
    )