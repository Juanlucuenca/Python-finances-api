import datetime
import requests

URL_UVA = "https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/"

def uva_parsing():
    uva_history_price = requests.get(URL_UVA).json()

    uva_of_the_current_day = next(
        (item for item in uva_history_price if item["fecha"] == datetime.datetime.now().strftime("%d-%m-%Y")), None)
    
    return uva_of_the_current_day