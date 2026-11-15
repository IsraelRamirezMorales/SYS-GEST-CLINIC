from src.database.access import require_patient_access
from src.database.db import get_cursor
from src.utils.security import CurrentUser

_PRICES = {"Consulta": 800, "Terapia": 350, "Alberca": 400}


def add_sesions(user: CurrentUser, id_patient, entry_time, entry_date, sesion_type):
    state = "Sin empezar"
    amount_to_pay = _PRICES[sesion_type]

    with get_cursor() as cur:
        patient = require_patient_access(cur, user, id_patient)
        id_doctor = patient["doctor_charge"]

        # Empleado que realmente atiende la sesión (regla de negocio existente).
        performing_employee = user.id_employees
        if sesion_type == "Alberca":
            performing_employee = 9  # Cristian
        elif sesion_type == "Terapia":
            if id_doctor == 5:
                performing_employee = 6  # Hugo
            elif id_doctor == 8:
                performing_employee = 7  # Monica
        elif sesion_type == "Consulta" and id_doctor is not None:
            performing_employee = id_doctor

        cur.execute(
            """
            INSERT INTO sesions (entry_date, sesion_type, id_patient, id_employees, entry_time, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_sesion
            """,
            (entry_date, sesion_type, id_patient, performing_employee, entry_time, state),
        )
        id_sesion = cur.fetchone()["id_sesion"]

        cur.execute(
            """
            INSERT INTO session_records
                (id_sesion, entry_date, entry_time, sesion_type, id_patient, id_employees, state)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (id_sesion, entry_date, entry_time, sesion_type, id_patient, performing_employee, state),
        )

        cur.execute(
            "UPDATE patients SET amount_to_pay = amount_to_pay + %s WHERE id_patient = %s",
            (amount_to_pay, id_patient),
        )
