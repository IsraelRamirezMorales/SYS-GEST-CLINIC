from src.database.access import require_patient_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def edit_patients_info(user: CurrentUser, id_patient, name, last_name, phone, amount_to_pay, doctor_sender=None):
    with get_cursor() as cur:
        require_patient_access(cur, user, id_patient)
        cur.execute(
            """
            UPDATE patients
            SET name = %s, last_name = %s, phone = %s, amount_to_pay = %s, doctor_sender = %s
            WHERE id_patient = %s
            """,
            (name, last_name, phone, amount_to_pay, doctor_sender, id_patient),
        )
