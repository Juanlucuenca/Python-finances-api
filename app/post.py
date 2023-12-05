import schedule
import time
from sqlmodel import Session
from main import create_mac

from database import engine


def tarea_programada():
    with Session(engine) as session:
        create_mac(session)


# Programar la tarea
schedule.every().day.at("12:00").do(tarea_programada)
schedule.every().day.at("15:00").do(tarea_programada)
schedule.every().day.at("16:00").do(tarea_programada)

# Bucle para ejecutar las tareas programadas
while True:
    schedule.run_pending()
    time.sleep(1)
