import datetime
import traceback
from fastapi import HTTPException
import requests

URL_UVA = "https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/"

def uva_parsing():
    try:
        uva_history_price = requests.get(URL_UVA).json()

        uva_of_the_current_day = next(
            (item for item in uva_history_price if item["fecha"] == datetime.datetime.now().strftime("%d-%m-%Y")), None)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error parsing dolar mayorista info: {e}")

    
    return uva_of_the_current_day