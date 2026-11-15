from datetime import date, time

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.add_sesion import add_sesions
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Id, SesionType

router = APIRouter(prefix="/add_sesion")


class NewSession(BaseModel):
    id_patient: Id
    entry_time: time
    entry_date: date
    sesion_type: SesionType


@router.post("/")
def add_sesion(data: NewSession, user: CurrentUser = Depends(get_current_user)):
    add_sesions(user, data.id_patient, data.entry_time, data.entry_date, data.sesion_type)
    return {"ok": True}
