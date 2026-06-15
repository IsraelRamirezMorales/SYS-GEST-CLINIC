from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from src.database.show_info import show_information


router = APIRouter(prefix="/show_info")

class InfoRequest(BaseModel):
    id_patient: int

@router.post("/")
def show_info(data:InfoRequest):
   return show_information(data.id_patient)
   
   
