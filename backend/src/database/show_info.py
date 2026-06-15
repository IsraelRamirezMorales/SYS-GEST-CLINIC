
from src.database.conection import *
from psycopg2.extras import RealDictCursor

def show_information(id_patient):
   
   

    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
                """
                SELECT imp_data FROM patients WHERE id_patient = %s
                
                """,
                (id_patient,)
                
            )
    info = cur.fetchone()
   
    cur.close()
    conn.close()
    if info is None:
     return {"info": ""}

    return {"info": info["imp_data"]}


