from fastapi import APIRouter
from src.database.reports import get_reports_data

router = APIRouter(prefix="/reports")

@router.get("/")
def read_reports(id_employees: int):
    return get_reports_data(id_employees)
