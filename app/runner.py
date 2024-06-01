import asyncio
from sqlalchemy import text
from sqlmodel import Session
from db.repository.save import save
from db.schemas import DolarDB, BonoDB, ObligacionDB
from db.database import engine
from services.scrapper_iol import iol_parsing
from services.scrapping_dolarhoy import scrapping_dolarhoy


async def scrap_and_update_dolars_periodically():
    while True:
        with Session(engine) as session:
            dolars_list = scrapping_dolarhoy()
            session.exec(text("DELETE FROM dolardb"))
            save(dolars_list, session, DolarDB)
        await asyncio.sleep(30)

async def scrap_and_update_bono_periodically():
    while True:
        with Session(engine) as session:
            bono_list = iol_parsing("bonos")
            session.exec(text("DELETE FROM bonodb"))
            save(bono_list, session, BonoDB) 
        await asyncio.sleep(400)

async def scrap_and_update_obligacion_periodically():
    while True:
        with Session(engine) as session:
            obligaciones_list = iol_parsing("obligaciones-negociables")
            session.exec(text("DELETE FROM obligaciondb"))
            save(obligaciones_list, session, ObligacionDB)
        await asyncio.sleep(400)

async def run_background_tasks():
    await asyncio.gather(
        scrap_and_update_dolars_periodically(),
        scrap_and_update_bono_periodically(),
        scrap_and_update_obligacion_periodically()
    )

asyncio.run(run_background_tasks())