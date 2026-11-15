from fastapi import APIRouter, Depends

from src.database.patients_appointments import patient_apponintment
from src.utils.security import CurrentUser, get_current_user

router = APIRouter(prefix="/patients_appointments")


@router.get("/")
def patients_apponintments(user: CurrentUser = Depends(get_current_user)):
    return patient_apponintment(user)
