from typing import Optional

from src.database.db import get_cursor


def update_profile_picture(id_employees: int, profile_picture: Optional[str]) -> None:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE employees SET profile_picture = %s WHERE id_employees = %s",
            (profile_picture, id_employees),
        )


def get_profile_picture_url(id_employees: int) -> Optional[str]:
    with get_cursor() as cur:
        cur.execute("SELECT profile_picture FROM employees WHERE id_employees = %s", (id_employees,))
        row = cur.fetchone()
    return row["profile_picture"] if row else None
