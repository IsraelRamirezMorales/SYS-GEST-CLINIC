from src.database.access import require_patient_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def update_note(user: CurrentUser, id_patient: int, imp_data: str):
    with get_cursor() as cur:
        require_patient_access(cur, user, id_patient)
        cur.execute("UPDATE patients SET imp_data = %s WHERE id_patient = %s", (imp_data, id_patient))
