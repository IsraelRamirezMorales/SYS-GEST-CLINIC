from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from typing import Optional

from src.database.add_patien import add_patient

router = APIRouter(prefix="/add_patients")


class LoginData(BaseModel):
    name: str
    last_name: str
    phone: str
    id_employees: int                
    doctor_selected: Optional[str] = None  
    instructions: Optional[str] = None
    aseguradora: Optional[str] = None
    doctor_sender: Optional[str] = None


@router.post("/")
def add_patients(data: LoginData):
    add_patient(
        data.name,
        data.last_name,
        data.phone,
        data.id_employees,
        data.instructions,
        data.doctor_selected,
        data.aseguradora,
        doctor_sender=data.doctor_sender
    )
