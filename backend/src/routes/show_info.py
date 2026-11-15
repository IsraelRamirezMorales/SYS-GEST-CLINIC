from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.database.show_info import show_information
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Id

router = APIRouter(prefix="/show_info")


class InfoRequest(BaseModel):
    id_patient: Id


@router.post("/")
def show_info(data: InfoRequest, user: CurrentUser = Depends(get_current_user)):
    return show_information(user, data.id_patient)
