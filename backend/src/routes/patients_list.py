from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from src.database.patients_list import patients_list


router = APIRouter(prefix="/patients_list")



@router.get("/")
def patient_list(id_employees: int):
   print(id_employees)
   return patients_list(id_employees)
   
   
