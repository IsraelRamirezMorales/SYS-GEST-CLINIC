import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

from src.routes.add_patients import router as add_patients  # noqa: E402
from src.routes.add_sesion import router as add_sesion  # noqa: E402
from src.routes.asistance import router as asistance  # noqa: E402
from src.routes.change_session_date import router as change_session_date  # noqa: E402
from src.routes.check_collision import router as check_collision  # noqa: E402
from src.routes.edit_patient_info import router as edit_patient_info  # noqa: E402
from src.routes.export_pdf import router as export_pdf_router  # noqa: E402
from src.routes.get_fisio_type import router as get_fisio_type  # noqa: E402
from src.routes.login import router as login_router  # noqa: E402
from src.routes.patients_appoinments import router as patients_appoinments  # noqa: E402
from src.routes.patients_list import router as patients_list  # noqa: E402
from src.routes.profile import router as profile_router  # noqa: E402
from src.routes.reports import router as reports_router  # noqa: E402
from src.routes.show_info import router as show_info  # noqa: E402
from src.routes.update_notes import router as update_notes  # noqa: E402

# La documentación interactiva expone el mapa completo de la API: solo se activa a propósito.
_docs_enabled = os.getenv("ENABLE_DOCS", "false").lower() == "true"

app = FastAPI(
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

_DEFAULT_ORIGINS = ",".join(
    [
        "https://cl-nica-remes-banz.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
)
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", _DEFAULT_ORIGINS).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    # La autenticación va en el header Authorization, no en cookies.
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    # Las respuestas contienen datos clínicos: no deben quedar en cachés.
    response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Se registra el detalle en el servidor; el cliente solo recibe un mensaje genérico.
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


app.include_router(login_router)
app.include_router(add_patients)
app.include_router(patients_list)
app.include_router(patients_appoinments)
app.include_router(add_sesion)
app.include_router(asistance)
app.include_router(show_info)
app.include_router(edit_patient_info)
app.include_router(update_notes)
app.include_router(get_fisio_type)
app.include_router(check_collision)
app.include_router(reports_router)
app.include_router(change_session_date)
app.include_router(profile_router)
app.include_router(export_pdf_router)
