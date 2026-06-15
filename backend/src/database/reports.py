from src.database.id_employee import get_id
from src.database.conection import *
from psycopg2.extras import RealDictCursor
from src.database.get_fisi_type import get_patient_info

def get_reports_data(id_employees):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)

    tipo_fisio = get_patient_info(id_employees)
    id_doctor = get_id(id_employees)

    # If not Acuática, we filter patients by doctor_charge
    is_acuatic = (tipo_fisio == 'Acuática')

    # ── Helper: fetch main type+state metrics ──────────────────────────────
    def fetch_metrics(interval_sql):
        if is_acuatic:
            query = f"""
                SELECT sesion_type, state, COUNT(*) as count
                FROM session_records
                WHERE {interval_sql}
                GROUP BY sesion_type, state;
            """
            cur.execute(query)
        else:
            query = f"""
                SELECT r.sesion_type, r.state, COUNT(*) as count
                FROM session_records r
                INNER JOIN patients p ON r.id_patient = p.id_patient
                WHERE {interval_sql} AND p.doctor_charge = %s
                GROUP BY r.sesion_type, r.state;
            """
            cur.execute(query, (id_doctor,))
        return cur.fetchall()

    # ── Helper: fetch per-doctor breakdown per type ────────────────────────
    # Always global (Acuática sees all; others see the types they manage which
    # are already scoped by their patient pool — but for the chart we want
    # a clinic-wide doctor breakdown so directors can see all).
    def fetch_by_doctor(interval_sql):
        query = f"""
            SELECT
                r.sesion_type,
                r.id_employees,
                e.name  AS doctor_name,
                e.last_name AS doctor_last,
                COUNT(*) AS count
            FROM session_records r
            LEFT JOIN employees e ON r.id_employees = e.id_employees
            WHERE {interval_sql}
            GROUP BY r.sesion_type, r.id_employees, e.name, e.last_name;
        """
        cur.execute(query)
        return cur.fetchall()

    # Intervals (PostgreSQL DATE_TRUNC)
    week_sql  = "entry_date >= DATE_TRUNC('week',  CURRENT_DATE)::DATE AND entry_date <= (DATE_TRUNC('week',  CURRENT_DATE) + INTERVAL '6 days')::DATE"
    month_sql = "entry_date >= DATE_TRUNC('month', CURRENT_DATE)::DATE AND entry_date <= (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'  - INTERVAL '1 day')::DATE"
    year_sql  = "entry_date >= DATE_TRUNC('year',  CURRENT_DATE)::DATE AND entry_date <= (DATE_TRUNC('year',  CURRENT_DATE) + INTERVAL '1 year'   - INTERVAL '1 day')::DATE"

    week_raw   = fetch_metrics(week_sql)
    month_raw  = fetch_metrics(month_sql)
    year_raw   = fetch_metrics(year_sql)

    week_doc   = fetch_by_doctor(week_sql)
    month_doc  = fetch_by_doctor(month_sql)
    year_doc   = fetch_by_doctor(year_sql)

    cur.close()
    conn.close()

    # ── Format main summary ────────────────────────────────────────────────
    def format_raw(raw_data):
        summary = {
            "total": 0,
            "types": {"Consulta": 0, "Terapia": 0, "Alberca": 0},
            "states": {"Sin empezar": 0, "Asistió": 0, "No Asistió": 0}
        }
        for item in raw_data:
            c      = int(item["count"])
            stype  = item["sesion_type"]
            sstate = item["state"]
            summary["total"] += c
            summary["types"][stype]   = summary["types"].get(stype, 0) + c
            summary["states"][sstate] = summary["states"].get(sstate, 0) + c
        return summary

    # ── Format per-doctor breakdown: { "Consulta": [{name, count},...], ... }
    def format_by_doctor(doc_data):
        result = {}
        for item in doc_data:
            stype = item["sesion_type"]
            name  = item["doctor_name"] or "Desconocido"
            c     = int(item["count"])
            if stype not in result:
                result[stype] = []
            result[stype].append({"name": name, "count": c})
        return result

    return {
        "week":  {**format_raw(week_raw),  "by_doctor": format_by_doctor(week_doc)},
        "month": {**format_raw(month_raw), "by_doctor": format_by_doctor(month_doc)},
        "year":  {**format_raw(year_raw),  "by_doctor": format_by_doctor(year_doc)},
    }
