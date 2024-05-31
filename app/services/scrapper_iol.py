from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from models.IolResponse import IolResponse
from utils.convert_to_numeric_value import convert_to_numeric_value


def iol_parsing(type: str) -> List[IolResponse]:
    # Configuración del navegador en modo headless para mayor rapidez
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Activar modo headless
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, requerido en Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Superar problemas de recursos limitados
    chrome_options.add_argument('start-maximized')  # Maximizar la ventana del navegador
    chrome_options.add_argument('--disable-extensions')  # Deshabilitar extensiones para mejorar el rendimiento
    chrome_options.add_argument("--log-level=3")  # Suprime los mensajes de consola de nivel INFO y por debajo

    # Iniciar el navegador con las opciones definidas
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://iol.invertironline.com/mercado/cotizaciones/argentina/{type}/todos")

    try:
        # Espera hasta que el elemento select esté presente en la página
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "cotizaciones_length"))
        )

        # Crea un objeto Select usando el elemento encontrado
        select_obj = Select(select_element)
        select_obj.select_by_value("-1")  # Selecciona todas las filas

        # Espera hasta que la tabla esté visible y completamente cargada
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "cotizaciones"))
        )

        # Extrae todas las filas de la tabla
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        datos_tabla = []

        # Procesa cada fila de la tabla
        for fila in filas:
            celdas = fila.find_elements(By.TAG_NAME, "td")
            fila_datos = []
            for index, celda in enumerate(celdas):
                if index == 0:  # Asume que el primer elemento puede contener un enlace
                    enlace = celda.find_element(By.TAG_NAME, "a") if celda.find_elements(By.TAG_NAME, "a") else None
                    simbolo = enlace.get_attribute("data-symbol") if enlace else "Symbol"
                    fila_datos.append(simbolo)
                else:
                    fila_datos.append(convert_to_numeric_value(celda.text))
            datos_tabla.append(fila_datos)

        encabezados = datos_tabla[0]
        encabezados = [encabezado.replace('\n', ' ').strip() for encabezado in encabezados]
        scrapped_data = [dict(zip(encabezados, fila)) for fila in datos_tabla[1:]]

        # Eliminar la última propiedad vacía de cada objeto
        for item in scrapped_data:
            if '' in item:
                del item['']

        # Ordenar los datos por el campo "Symbol"
        scrapped_data.sort(key=lambda x: x["Symbol"])
    finally:       
        driver.close()
        driver.quit()

    formatted_data: List[IolResponse] = []

    for data in scrapped_data:
        formatted_data.append(format_iol_data(data))

    return formatted_data

def format_iol_data(data: dict) -> IolResponse:
    return IolResponse(
        symbol=data.get('Symbol'),
        ultimo_operado=data.get('Último Operado'),
        variacion_diaria=data.get('Variación Diaria'),
        cantidad_compra=data.get('Cantidad Compra'),
        precio_compra=data.get('Precio Compra'),
        precio_venta=data.get('Precio Venta'),
        cantidad_venta=data.get('Cantidad Venta'),
        maximo=data.get('Máximo'),
        minimo=data.get('Mínimo'),
        ultimo_cierre=data.get('Último Cierre'),
        monto_operado=data.get('Monto Operado'),
        tir=data.get('T. I. R.'),
        duracion_md=data.get('Duración (MD)')
    )