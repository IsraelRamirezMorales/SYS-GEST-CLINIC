from fastapi import APIRouter
from src.database.edit_patient_info import edit_patients_info
from pydantic import BaseModel
from datetime import date
from typing import Optional



router = APIRouter(prefix="/edit_patient_info")

class LoginData(BaseModel):
    id_patient : int
    name: str
    last_name: str
    phone: str
    amount_to_pay : int
    doctor_sender: Optional[str] = None
  
    

@router.post("/")
def edit_patient_info(data: LoginData):
   return edit_patients_info(
       data.id_patient,
       data.name,
       data.last_name,
       data.phone,
       data.amount_to_pay,
       doctor_sender=data.doctor_sender
   )
   
   