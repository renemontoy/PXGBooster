from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.endpoints import router as upload_router
import os

app = FastAPI()

# Obtén el dominio del frontend desde una variable de entorno (para desarrollo y producción)
#frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


origins = [
    "https://pxgbooster.onrender.com",  # Tu frontend en Render
    "http://localhost:5173",  
    "http://localhost:8000",                   # Para desarrollo local con Vite
]
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(upload_router, prefix="/api")