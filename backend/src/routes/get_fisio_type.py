from fastapi import APIRouter, Depends

from src.utils.security import CurrentUser, get_current_user

router = APIRouter(prefix="/fisio_type")


@router.get("/")
def get_fisio(user: CurrentUser = Depends(get_current_user)):
    # Viene del token: no hace falta consultar la BD.
    return {"fisio_type": user.fisio_type}
