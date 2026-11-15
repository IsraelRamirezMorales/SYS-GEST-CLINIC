from datetime import date, time

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.change_session_date import update_session_date
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Id

router = APIRouter(prefix="/change_session_date")


class ChangeDateData(BaseModel):
    id_sesion: Id
    entry_date: date
    entry_time: time


@router.post("/")
def change_session_date(data: ChangeDateData, user: CurrentUser = Depends(get_current_user)):
    update_session_date(user, data.id_sesion, data.entry_date, data.entry_time)
    return {"ok": True}
