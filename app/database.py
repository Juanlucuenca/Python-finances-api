from sqlmodel import SQLModel, create_engine
from sqlmodel import Session
from pathlib import Path

# Obtén el directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

SQLITE_FILE_NAME = "dollarApi.db"
sqlite_url = f"sqlite:///{BASE_DIR}/{SQLITE_FILE_NAME}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
