from src.database.access import require_patient_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def show_information(user: CurrentUser, id_patient: int):
    with get_cursor() as cur:
        require_patient_access(cur, user, id_patient)
        cur.execute("SELECT imp_data FROM patients WHERE id_patient = %s", (id_patient,))
        row = cur.fetchone()
    return {"info": (row["imp_data"] if row else "") or ""}
