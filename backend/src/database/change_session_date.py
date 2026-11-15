from datetime import date, time

from src.database.access import require_session_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def update_session_date(user: CurrentUser, id_sesion: int, entry_date: date, entry_time: time):
    with get_cursor() as cur:
        require_session_access(cur, user, id_sesion)
        cur.execute(
            "UPDATE sesions SET entry_date = %s, entry_time = %s WHERE id_sesion = %s",
            (entry_date, entry_time, id_sesion),
        )
        cur.execute(
            """
            UPDATE session_records
            SET entry_date = %s, entry_time = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id_sesion = %s
            """,
            (entry_date, entry_time, id_sesion),
        )
