from fastapi import APIRouter
from pydantic import BaseModel
from src.database.menu import foto_menu

router = APIRouter(prefix="/menu")

class LoginData(BaseModel):
    name: str
    password: str

@router.post("/")
def login(data: LoginData):
    return{
        "name": data.name
    }

