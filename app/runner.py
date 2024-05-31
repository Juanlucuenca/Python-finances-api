import asyncio
from sqlalchemy import text
from sqlmodel import Session
from db.repository.save_bonos_to_db import save_bonos_to_db
from db.repository.save_dolars_to_db import save_dolars_to_db
from db.repository.save_obligaciones_to_db import save_obligaciones_to_db
from db.database import engine
from services.scrapper_iol import iol_parsing
from services.scrapping_dolarhoy import scrapping_dolarhoy


async def scrap_and_update_dolars_periodically():
    while True:
        with Session(engine) as session:
            dolars_list = scrapping_dolarhoy()
            print(dolars_list)
            session.exec(text("DELETE FROM dolardb"))
            save_dolars_to_db(dolars_list, session)
            print("Dolars actualizados correctamente")
        await asyncio.sleep(30)

async def scrap_and_update_bono_periodically():
    while True:
        with Session(engine) as session:
            bono_list = iol_parsing("bonos")
            session.exec(text("DELETE FROM bonodb"))
            save_bonos_to_db(bono_list, session)
            print("bonos actualizados correctamente")
            
        await asyncio.sleep(600)

async def scrap_and_update_obligacion_periodically():
    while True:
        with Session(engine) as session:
            obligaciones_list = iol_parsing("obligaciones-negociables")
            session.exec(text("DELETE FROM obligaciondb"))
            save_obligaciones_to_db(obligaciones_list, session)
            print("Obligaciones actualizados correctamente")
        await asyncio.sleep(600)

async def run_background_tasks():
    await asyncio.gather(
        scrap_and_update_dolars_periodically(),
        scrap_and_update_bono_periodically(),
        scrap_and_update_obligacion_periodically()
    )

asyncio.run(run_background_tasks())