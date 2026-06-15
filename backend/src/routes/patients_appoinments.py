from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from src.database.patients_appointments import patient_apponintment


router = APIRouter(prefix="/patients_appointments")




@router.get("/")
def patients_apponintments(id_employees:int):
   return patient_apponintment(id_employees)
   
   
