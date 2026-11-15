from src.database.access import can_see_doctor_charge
from src.database.db import get_cursor
from src.utils.security import CurrentUser


def get_collisions(user: CurrentUser, entry_date, entry_time, sesion_type):
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT p.name, p.last_name, p.doctor_charge, s.sesion_type
            FROM sesions s
            INNER JOIN patients p ON s.id_patient = p.id_patient
            WHERE s.entry_date = %s AND s.entry_time = %s AND s.sesion_type = %s
              AND s.state = 'Sin empezar'
            """,
            (entry_date, entry_time, sesion_type),
        )
        rows = cur.fetchall()

    # Los nombres de pacientes que el usuario no puede ver se ocultan.
    result = []
    for r in rows:
        visible = can_see_doctor_charge(user, r["doctor_charge"])
        result.append(
            {
                "name": r["name"] if visible else "Paciente de otra área",
                "last_name": r["last_name"] if visible else "",
                "sesion_type": r["sesion_type"],
            }
        )
    return result
