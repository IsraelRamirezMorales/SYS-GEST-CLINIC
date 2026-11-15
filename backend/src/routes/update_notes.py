from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.update_notes import update_note
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Id, LongText

router = APIRouter(prefix="/update_notes")


class NotesData(BaseModel):
    id_patient: Id
    imp_data: LongText


@router.post("/")
def update_notes(data: NotesData, user: CurrentUser = Depends(get_current_user)):
    update_note(user, data.id_patient, data.imp_data)
    return {"ok": True}
