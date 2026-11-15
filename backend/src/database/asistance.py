from src.database.access import require_session_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def asistances(user: CurrentUser, id_sesion: int, attended: bool):
    state = "Asistió" if attended else "No Asistió"
    with get_cursor() as cur:
        require_session_access(cur, user, id_sesion)
        cur.execute("UPDATE sesions SET state = %s WHERE id_sesion = %s", (state, id_sesion))
        cur.execute(
            "UPDATE session_records SET state = %s, updated_at = CURRENT_TIMESTAMP WHERE id_sesion = %s",
            (state, id_sesion),
        )
