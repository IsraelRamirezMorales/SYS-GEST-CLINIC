from fastapi import APIRouter, Depends

from src.database.reports import get_reports_data
from src.utils.security import CurrentUser, get_current_user

router = APIRouter(prefix="/reports")


@router.get("/")
def read_reports(user: CurrentUser = Depends(get_current_user)):
    return get_reports_data(user)
