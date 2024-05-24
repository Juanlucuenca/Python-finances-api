from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


from enum import Enum

class Inversion_type(Enum):
    BONOS = "bonos"
    OBLIGACIONES = "obligaciones-negociables"

def iol_parsing():
    # Configuración del navegador en modo headless para mayor rapidez
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Activar modo headless
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, requerido en Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Superar problemas de recursos limitados
    chrome_options.add_argument('start-maximized')  # Maximizar la ventana del navegador
    chrome_options.add_argument('--disable-extensions')  # Deshabilitar extensiones para mejorar el rendimiento

    # Iniciar el navegador con las opciones definidas
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://iol.invertironline.com/mercado/cotizaciones/argentina/bonos/todos")

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
                    fila_datos.append(celda.text)
            datos_tabla.append(fila_datos)

        # Preparar los datos en formato JSON (suponiendo que la primera fila son encabezados)
        encabezados = datos_tabla[0]
        datos_json = [dict(zip(encabezados, fila)) for fila in datos_tabla[1:]]

    finally:
        driver.quit()  # Asegúrate de cerrar el navegador sin importar lo que pase

    return datos_json

print(iol_parsing())