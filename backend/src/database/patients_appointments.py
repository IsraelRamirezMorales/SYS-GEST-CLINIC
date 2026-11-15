from src.database.db import get_cursor
from src.utils.security import CurrentUser

# El front solo muestra:
#   - sesiones 'Sin empezar' de cualquier fecha (calendario y lista de citas)
#   - sesiones atendidas / no atendidas del mes actual (búsqueda)
# Antes se enviaba todo el historial. Se deja un día de margen por la zona horaria
# (CURRENT_DATE es UTC en el servidor y el front filtra en hora local).
_QUERY = """
    SELECT p.id_patient, p.name, p.last_name, p.phone, p.amount_to_pay, p.aseguradora,
           p.doctor_charge, s.id_sesion, s.entry_date, s.entry_time, s.state, s.sesion_type
    FROM sesions s
    INNER JOIN patients p ON s.id_patient = p.id_patient
    WHERE (
            s.state = 'Sin empezar'
         OR s.entry_date >= (DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 day')::DATE
          )
      {scope}
    ORDER BY s.entry_time ASC
"""


def patient_apponintment(user: CurrentUser):
    with get_cursor() as cur:
        if user.is_acuatic:
            cur.execute(_QUERY.format(scope=""))
        else:
            cur.execute(_QUERY.format(scope="AND p.doctor_charge = %s"), (user.scope_doctor,))
        return cur.fetchall()
