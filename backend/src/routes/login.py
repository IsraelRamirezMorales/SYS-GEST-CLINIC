from fastapi import APIRouter
from pydantic import BaseModel
from src.database.login import confirmation_login

router = APIRouter(prefix="/login")

class LoginData(BaseModel):
    username: str
    password: str
    

@router.post("/")
def login(data: LoginData):
    try:
        user = confirmation_login(data.username, data.password)

        if not user:
            return {"ok": False}

        if len(user) < 5:
            print("LOGIN ERROR: unexpected user format", user)
            return {"ok": False}

        id_employees, username, name, role, last_name, profile_picture = user

        return {
            "ok": True,
            "id_employees": id_employees,
            "username": username,
            "name": name,
            "last_name": last_name,
            "role": role,
            "profile_picture": profile_picture
        }

    except Exception as e:
        print("LOGIN EXCEPTION:", e)
        return {"ok": False, "error": "internal"}
