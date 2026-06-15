from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date, time
from src.database.add_sesion import add_sesions
from typing import Optional


router = APIRouter(prefix="/add_sesion")

class LoginData(BaseModel):
    id_patient : int
    entry_time: time
    entry_date: date
    sesion_type: str
    id_employees: int
    

@router.post("/")
def add_sesion(data: LoginData):
   add_sesions(data.id_patient,data.entry_time,data.entry_date,data.sesion_type,data.id_employees)

   
