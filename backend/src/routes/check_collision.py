from datetime import date, time

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.check_collision import get_collisions
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import SesionType

router = APIRouter(prefix="/check_collision")


class CollisionCheckData(BaseModel):
    entry_date: date
    entry_time: time
    sesion_type: SesionType


@router.post("/")
def check_collision(data: CollisionCheckData, user: CurrentUser = Depends(get_current_user)):
    return {"collisions": get_collisions(user, data.entry_date, data.entry_time, data.sesion_type)}
