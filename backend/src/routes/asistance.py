from fastapi import APIRouter
from src.database.asistance import asistances
from pydantic import BaseModel



router = APIRouter(prefix="/asistance")

class LoginData(BaseModel):
    id_sesion : int
    asistance : bool
    

@router.post("/")
def asistance(data: LoginData):
   return asistances(data.id_sesion,data.asistance)
   
   