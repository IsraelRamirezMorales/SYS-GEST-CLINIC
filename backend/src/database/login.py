import logging

from src.database.db import get_cursor
from src.utils.security import (
    burn_password_check,
    get_password_hash,
    is_hashed,
    verify_password,
)

logger = logging.getLogger(__name__)


def confirmation_login(username: str, password: str):
    """
    Devuelve los datos públicos del empleado si las credenciales son válidas, o None.
    Migra a bcrypt las contraseñas legacy en texto plano en el mismo login.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id_employees, username, name, last_name, role, fisio_type,
                   assigned_doctor, password, profile_picture
            FROM employees
            WHERE username = %s
            """,
            (username,),
        )
        row = cur.fetchone()

        if row is None:
            burn_password_check()
            return None

        if not verify_password(password, row["password"]):
            return None

        if not is_hashed(row["password"]) and len(password.encode("utf-8")) <= 72:
            try:
                cur.execute(
                    "UPDATE employees SET password = %s WHERE id_employees = %s",
                    (get_password_hash(password), row["id_employees"]),
                )
            except Exception:
                logger.exception("No se pudo migrar la contraseña legacy a hash")
                raise

    role = row["role"]
    scope_doctor = row["id_employees"]
    if role == "Fisio" and row["assigned_doctor"] is not None:
        scope_doctor = row["assigned_doctor"]

    return {
        "id_employees": row["id_employees"],
        "username": row["username"],
        "name": row["name"],
        "last_name": row["last_name"],
        "role": role,
        "fisio_type": row["fisio_type"],
        "profile_picture": row["profile_picture"],
        "scope_doctor": scope_doctor,
    }
