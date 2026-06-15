from fastapi import APIRouter
from src.database.update_notes import update_note
from pydantic import BaseModel



router = APIRouter(prefix="/update_notes")

class LoginData(BaseModel):
    id_patient: int
    imp_data : str
    

@router.post("/")
def update_notes(data: LoginData):
   print(data)
   return update_note(data.id_patient,data.imp_data)
   
   