from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.add_patien import add_patient
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import LongText, PersonName, Phone, ShortText

router = APIRouter(prefix="/add_patients")


class NewPatient(BaseModel):
    name: PersonName
    last_name: PersonName
    phone: Phone
    doctor_selected: Optional[ShortText] = None
    instructions: Optional[LongText] = None
    aseguradora: Optional[ShortText] = None
    doctor_sender: Optional[ShortText] = None


@router.post("/")
def add_patients(data: NewPatient, user: CurrentUser = Depends(get_current_user)):
    add_patient(
        user,
        data.name,
        data.last_name,
        data.phone,
        data.instructions,
        data.doctor_selected,
        data.aseguradora,
        doctor_sender=data.doctor_sender,
    )
    return {"ok": True}
