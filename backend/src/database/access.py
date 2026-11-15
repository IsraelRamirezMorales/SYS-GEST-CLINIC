"""
Reglas de autorización sobre pacientes y sesiones.

Regla de negocio (la misma que ya usaban los listados):
- Fisio acuático: ve a todos los pacientes.
- Resto: solo pacientes cuyo doctor_charge es su doctor (scope_doctor).
"""
from fastapi import HTTPException, status

from src.utils.security import CurrentUser

_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")


def can_see_doctor_charge(user: CurrentUser, doctor_charge) -> bool:
    return user.is_acuatic or doctor_charge == user.scope_doctor


def require_patient_access(cur, user: CurrentUser, id_patient: int) -> dict:
    """Devuelve la fila del paciente o lanza 404 (no 403, para no revelar que existe)."""
    cur.execute(
        "SELECT id_patient, doctor_charge FROM patients WHERE id_patient = %s",
        (id_patient,),
    )
    row = cur.fetchone()
    if row is None or not can_see_doctor_charge(user, row["doctor_charge"]):
        raise _NOT_FOUND
    return row


def require_session_access(cur, user: CurrentUser, id_sesion: int) -> dict:
    cur.execute(
        """
        SELECT s.id_sesion, s.id_patient, p.doctor_charge
        FROM sesions s
        INNER JOIN patients p ON p.id_patient = s.id_patient
        WHERE s.id_sesion = %s
        """,
        (id_sesion,),
    )
    row = cur.fetchone()
    if row is None or not can_see_doctor_charge(user, row["doctor_charge"]):
        raise _NOT_FOUND
    return row
