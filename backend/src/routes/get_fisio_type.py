from fastapi import APIRouter
from src.database.get_fisi_type import get_patient_info

router = APIRouter(prefix="/fisio_type")

@router.get("/")
def get_fisio(id_employees: int):
    return {
        "fisio_type": get_patient_info(id_employees)
    }
