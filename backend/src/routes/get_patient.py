from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from src.database.get_patient import get_patient_info


router = APIRouter(prefix="/get_patient")



@router.get("/")
def patient_list(id_patient:int):
   return get_patient_info(id_patient)
   