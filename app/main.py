from fastapi import FastAPI
from fastapi.responses import JSONResponse
from db.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from router import bonos, obligaciones, cotizaciones, analisis
import subprocess

app = FastAPI(
    title="Finance Apis",
    description="APIs para obtener informacion financiera de bonos, obligaciones, cotizaciones y analisis de mercado",
    version="v2",
    )

# Ruta completa al script runner.py
script_path = "app/runner.py"

# Directorio desde el cual se debe ejecutar el script
working_directory = "."

@app.on_event("startup")
async def startup_event():
    subprocess.Popen(["python",script_path], cwd=working_directory)
    create_db_and_tables()

# Configuracion de rutas nuevas
app.include_router(cotizaciones.router, prefix="/api/v2/cotizaciones", tags=["Cotizaciones"])
app.include_router(bonos.router, prefix="/api/v2/bonos", tags=["bonos"])
app.include_router(obligaciones.router, prefix="/api/v2/obligaciones", tags=["Obligaciones"])
app.include_router(analisis.router, prefix="/api/v2/analisis", tags=["Analisis"])

# Añadimos CORS para permitir el acceso desde cualquier origen
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CustomErrorHandler(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={"message": "An unexpected error occurred"}
            )
        return response

app.add_middleware(CustomErrorHandler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 

