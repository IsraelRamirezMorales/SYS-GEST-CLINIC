from src.database.db import get_cursor
from src.utils.security import CurrentUser

# Solo las columnas que usa el front (doctor_charge e imp_data no se envían).
_COLUMNS = "id_patient, name, last_name, phone, doctor_sender, amount_to_pay, aseguradora"


def patients_list(user: CurrentUser):
    with get_cursor() as cur:
        if user.is_acuatic:
            cur.execute(f"SELECT {_COLUMNS} FROM patients ORDER BY name ASC")
        else:
            cur.execute(
                f"SELECT {_COLUMNS} FROM patients WHERE doctor_charge = %s ORDER BY name ASC",
                (user.scope_doctor,),
            )
        return cur.fetchall()
