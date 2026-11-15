from src.database.access import require_patient_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def get_pdf_data(user: CurrentUser, id_patient: int):
    """Solo las columnas que se imprimen en el PDF."""
    with get_cursor() as cur:
        require_patient_access(cur, user, id_patient)
        cur.execute(
            """
            SELECT p.name, p.last_name, p.phone, p.doctor_sender, p.aseguradora,
                   e.name AS doctor_name, e.last_name AS doctor_last_name
            FROM patients p
            LEFT JOIN employees e ON p.doctor_charge = e.id_employees
            WHERE p.id_patient = %s
            """,
            (id_patient,),
        )
        patient = cur.fetchone()
        cur.execute(
            "SELECT name, last_name FROM employees WHERE id_employees = %s",
            (user.id_employees,),
        )
        employee = cur.fetchone()
    return patient, employee
