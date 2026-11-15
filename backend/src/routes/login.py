import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, StringConstraints

from src.database.login import confirmation_login
from src.utils.security import CurrentUser, create_access_token, login_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/login")


class LoginData(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


@router.post("/")
def login(data: LoginData, request: Request):
    ip = request.client.host if request.client else "unknown"

    if login_rate_limiter.is_blocked(data.username, ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Intenta de nuevo en unos minutos.",
        )

    user = confirmation_login(data.username, data.password)
    if not user:
        login_rate_limiter.register_failure(data.username, ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    login_rate_limiter.reset(data.username)

    token = create_access_token(
        CurrentUser(
            id_employees=user["id_employees"],
            role=user["role"],
            fisio_type=user["fisio_type"],
            scope_doctor=user["scope_doctor"],
        )
    )

    return {
        "ok": True,
        "access_token": token,
        "token_type": "bearer",
        "id_employees": user["id_employees"],
        "username": user["username"],
        "name": user["name"],
        "last_name": user["last_name"],
        "role": user["role"],
        "fisio_type": user["fisio_type"],
        "profile_picture": user["profile_picture"],
    }
