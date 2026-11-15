from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.asistance import asistances
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Id

router = APIRouter(prefix="/asistance")


class AttendanceData(BaseModel):
    id_sesion: Id
    asistance: bool


@router.post("/")
def asistance(data: AttendanceData, user: CurrentUser = Depends(get_current_user)):
    asistances(user, data.id_sesion, data.asistance)
    return {"ok": True}
