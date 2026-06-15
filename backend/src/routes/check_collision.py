from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date, time
from src.database.check_collision import get_collisions

router = APIRouter(prefix="/check_collision")

class CollisionCheckData(BaseModel):
    entry_date: date
    entry_time: time
    sesion_type: str

@router.post("/")
def check_collision(data: CollisionCheckData):
    collisions = get_collisions(data.entry_date, data.entry_time, data.sesion_type)
    return {"collisions": collisions}
