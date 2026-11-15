from typing import Optional

from fastapi import HTTPException, status

from src.database.db import get_cursor
from src.utils.security import CurrentUser


def add_patient(
    user: CurrentUser,
    name: str,
    last_name: str,
    phone: str,
    instructions: Optional[str],
    doctor_selected: Optional[str] = None,
    aseguradora: Optional[str] = None,
    doctor_sender: Optional[str] = None,
):
    with get_cursor() as cur:
        if doctor_selected:
            # Solo los fisios acuáticos eligen doctora; el resto queda con su propio alcance.
            if not user.is_acuatic:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "No puedes asignar otra doctora")
            cur.execute(
                "SELECT id_employees FROM employees WHERE name = %s AND role = 'Doctor'",
                (doctor_selected,),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Doctora no válida")
            doctor_charge = row["id_employees"]
        else:
            doctor_charge = user.scope_doctor

        cur.execute(
            """
            INSERT INTO patients
                (name, last_name, phone, amount_to_pay, doctor_charge, imp_data, aseguradora, doctor_sender)
            VALUES (%s, %s, %s, 0, %s, %s, %s, %s)
            """,
            (name, last_name, phone, doctor_charge, instructions or "", aseguradora or "", doctor_sender),
        )
