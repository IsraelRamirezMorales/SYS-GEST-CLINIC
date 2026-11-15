from src.database.db import get_cursor
from src.utils.security import CurrentUser

# Límites de semana / mes / año actuales. Antes eran 6 consultas (3 periodos x 2);
# ahora son 2 consultas con COUNT(*) FILTER sobre el rango que cubre los tres periodos.
_BOUNDS_CTE = """
    WITH b AS (
        SELECT DATE_TRUNC('week',  CURRENT_DATE)::DATE                                        AS ws,
               (DATE_TRUNC('week',  CURRENT_DATE) + INTERVAL '6 days')::DATE                  AS we,
               DATE_TRUNC('month', CURRENT_DATE)::DATE                                        AS ms,
               (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day')::DATE AS me,
               DATE_TRUNC('year',  CURRENT_DATE)::DATE                                        AS ys,
               (DATE_TRUNC('year',  CURRENT_DATE) + INTERVAL '1 year'  - INTERVAL '1 day')::DATE AS ye
    )
"""

_PERIOD_COUNTS = """
    COUNT(*) FILTER (WHERE r.entry_date BETWEEN b.ws AND b.we) AS week,
    COUNT(*) FILTER (WHERE r.entry_date BETWEEN b.ms AND b.me) AS month,
    COUNT(*) FILTER (WHERE r.entry_date BETWEEN b.ys AND b.ye) AS year
"""

_RANGE = "r.entry_date BETWEEN LEAST(b.ws, b.ys) AND GREATEST(b.we, b.ye)"

_PERIODS = ("week", "month", "year")


def get_reports_data(user: CurrentUser):
    with get_cursor() as cur:
        if user.is_acuatic:
            cur.execute(
                f"""{_BOUNDS_CTE}
                SELECT r.sesion_type, r.state, {_PERIOD_COUNTS}
                FROM session_records r CROSS JOIN b
                WHERE {_RANGE}
                GROUP BY r.sesion_type, r.state
                """
            )
        else:
            cur.execute(
                f"""{_BOUNDS_CTE}
                SELECT r.sesion_type, r.state, {_PERIOD_COUNTS}
                FROM session_records r
                CROSS JOIN b
                INNER JOIN patients p ON r.id_patient = p.id_patient
                WHERE {_RANGE} AND p.doctor_charge = %s
                GROUP BY r.sesion_type, r.state
                """,
                (user.scope_doctor,),
            )
        metrics = cur.fetchall()

        # Desglose por empleado de toda la clínica (decisión de negocio existente).
        cur.execute(
            f"""{_BOUNDS_CTE}
            SELECT r.sesion_type, r.id_employees, e.name AS doctor_name, {_PERIOD_COUNTS}
            FROM session_records r
            CROSS JOIN b
            LEFT JOIN employees e ON r.id_employees = e.id_employees
            WHERE {_RANGE}
            GROUP BY r.sesion_type, r.id_employees, e.name
            """
        )
        by_doctor = cur.fetchall()

    result = {}
    for period in _PERIODS:
        summary = {
            "total": 0,
            "types": {"Consulta": 0, "Terapia": 0, "Alberca": 0},
            "states": {"Sin empezar": 0, "Asistió": 0, "No Asistió": 0},
        }
        for item in metrics:
            c = int(item[period])
            if not c:
                continue
            summary["total"] += c
            summary["types"][item["sesion_type"]] = summary["types"].get(item["sesion_type"], 0) + c
            summary["states"][item["state"]] = summary["states"].get(item["state"], 0) + c

        doctors = {}
        for item in by_doctor:
            c = int(item[period])
            if not c:
                continue
            doctors.setdefault(item["sesion_type"], []).append(
                {"name": item["doctor_name"] or "Desconocido", "count": c}
            )

        result[period] = {**summary, "by_doctor": doctors}
    return result
