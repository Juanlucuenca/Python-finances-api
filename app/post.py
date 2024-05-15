import datetime
import schedule
import time
from sqlmodel import Session
from main import create_mac, guardar_dolares

from database import engine


def tarea_programada():
    with Session(engine) as session:
        create_mac(session)


def tarea_programada_dolares():
    # hora_actual = datetime.now().time()
    # inicio = hora_actual.replace(hour=12, minute=0, second=0, microsecond=0)
    # fin = hora_actual.replace(hour=16, minute=0, second=0, microsecond=0)
    # # Verificar si la hora actual está dentro del rango
    # if inicio <= hora_actual <= fin:
    with Session(engine) as session:
        guardar_dolares(session)


# Programar la tarea
schedule.every().day.at("12:00").do(tarea_programada)
schedule.every().day.at("15:00").do(tarea_programada)
schedule.every().day.at("16:00").do(tarea_programada)

# Programar tarea_programada_dolares para que se ejecute cada 5 minutos
schedule.every(1).minutes.do(tarea_programada_dolares)

# Bucle para ejecutar las tareas programadas
while True:
    schedule.run_pending()
    time.sleep(1)
