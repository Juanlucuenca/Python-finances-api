from fastapi import FastAPI
from database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from router import bonos, obligaciones, cotizaciones, analisis

app = FastAPI()

app.include_router(bonos.router, prefix="/api/v2/bonos", tags=["bonos"])
app.include_router(obligaciones.router, prefix="/api/v2/obligaciones", tags=["Obligaciones"])
app.include_router(analisis.router, prefix="/api/v2/analisis", tags=["Analisis"])
app.include_router(cotizaciones.router, prefix="/api/v2/cotizaciones", tags=["Cotizaciones"])

# Añadimos CORS para permitir el acceso desde cualquier origen
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    create_db_and_tables()