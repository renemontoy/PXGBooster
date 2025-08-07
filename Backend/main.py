from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router as upload_router
import os

app = FastAPI()

# Obtén el dominio del frontend desde una variable de entorno (para desarrollo y producción)
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(upload_router, prefix="/api")