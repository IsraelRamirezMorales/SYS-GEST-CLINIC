from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.database.change_session_date import update_session_date

router = APIRouter(prefix="/change_session_date")

class ChangeDateData(BaseModel):
    id_sesion: int
    entry_date: str
    entry_time: str

@router.post("/")
def change_session_date(data: ChangeDateData):
    try:
        update_session_date(data.id_sesion, data.entry_date, data.entry_time)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
