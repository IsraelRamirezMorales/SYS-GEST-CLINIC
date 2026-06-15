from src.database.conection import *
import psycopg2

def asistances(id_sesion,flag):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    try:
     if flag:
        cur.execute(
            """
            UPDATE sesions  SET state ='Asistió' WHERE id_sesion = %s;
            """,
            (id_sesion, )
        )
        cur.execute(
            """
            UPDATE session_records  SET state ='Asistió', updated_at = CURRENT_TIMESTAMP WHERE id_sesion = %s;
            """,
            (id_sesion, )
        )
     else:
        cur.execute(
            """
            UPDATE sesions  SET state ='No Asistió' WHERE id_sesion = %s;
            """,
            (id_sesion, )
        )
        cur.execute(
            """
            UPDATE session_records  SET state ='No Asistió', updated_at = CURRENT_TIMESTAMP WHERE id_sesion = %s;
            """,
            (id_sesion, )
        )

     conn.commit()


    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
    finally:
        cur.close()
        conn.close()

    
