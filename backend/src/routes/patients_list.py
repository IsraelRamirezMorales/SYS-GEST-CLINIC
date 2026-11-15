from fastapi import APIRouter, Depends

from src.database.patients_list import patients_list
from src.utils.security import CurrentUser, get_current_user

router = APIRouter(prefix="/patients_list")


@router.get("/")
def patient_list(user: CurrentUser = Depends(get_current_user)):
    return patients_list(user)
