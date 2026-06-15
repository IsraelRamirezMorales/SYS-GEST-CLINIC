import psycopg2
from src.database.conection import getconection

def update_session_date(id_sesion: int, entry_date: str, entry_time: str):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE sesions
            SET entry_date = %s, entry_time = %s
            WHERE id_sesion = %s;
            """,
            (entry_date, entry_time, id_sesion)
        )
        cur.execute(
            """
            UPDATE session_records
            SET entry_date = %s, entry_time = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id_sesion = %s;
            """,
            (entry_date, entry_time, id_sesion)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
