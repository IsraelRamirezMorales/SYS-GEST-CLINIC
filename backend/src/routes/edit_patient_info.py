from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.edit_patient_info import edit_patients_info
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Amount, Id, PersonName, Phone, ShortText

router = APIRouter(prefix="/edit_patient_info")


class EditPatient(BaseModel):
    id_patient: Id
    name: PersonName
    last_name: PersonName
    phone: Phone
    amount_to_pay: Amount
    doctor_sender: Optional[ShortText] = None


@router.post("/")
def edit_patient_info(data: EditPatient, user: CurrentUser = Depends(get_current_user)):
    edit_patients_info(
        user,
        data.id_patient,
        data.name,
        data.last_name,
        data.phone,
        data.amount_to_pay,
        doctor_sender=data.doctor_sender or None,
    )
    return {"ok": True}
