import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.routes.risk_routes import router as risk_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("risk_matrix")

app = FastAPI(
    title="Risk Matrix Generator API",
    description=(
        "API REST para la gestión de riesgos de activos de información. "
        "Implementa la fórmula Riesgo = Probabilidad × Impacto con "
        "clasificación de activos CIA y recomendación automática de controles "
        "alineados con ISO/IEC 27001:2022 y NIST CSF 2.0."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,https://yardka.github.io")
origins_list = [o.strip() for o in _allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router, prefix="/api/v1", tags=["Risk Engine"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )


@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "ok",
        "message": "Risk Matrix Generator API está en línea.",
        "version": "0.1.0",
        "docs": "/docs",
    }
