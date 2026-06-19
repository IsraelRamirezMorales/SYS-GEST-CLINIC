
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

from src.routes.login import router as login_router
from src.routes.add_patients import router as add_patients
from src.routes.patients_list import router as patients_list
from src.routes.patients_appoinments import router as patients_appoinments
from src.routes.add_sesion import router as add_sesion
from src.routes.asistance import router as asistance
from src.routes.show_info import router as show_info
from src.routes.edit_patient_info import router as edit_patient_info
from src.routes.get_patient import router as get_patient
from src.routes.update_notes import router as update_notes
from src.routes.get_fisio_type import router as get_fisio_type
from src.routes.check_collision import router as check_collision
from src.routes.reports import router as reports_router
from src.routes.change_session_date import router as change_session_date
from src.routes.profile import router as profile_router
from src.routes.export_pdf import router as export_pdf_router

app = FastAPI()
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    return JSONResponse(status_code=200)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cl-nica-remes-banz.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(add_patients)
app.include_router(patients_list)
app.include_router(patients_appoinments)
app.include_router(add_sesion)
app.include_router(asistance)
app.include_router(show_info)
app.include_router(edit_patient_info)
app.include_router(get_patient)
app.include_router(update_notes)
app.include_router(get_fisio_type)
app.include_router(check_collision)
app.include_router(reports_router)
app.include_router(change_session_date)
app.include_router(profile_router)
app.include_router(export_pdf_router)