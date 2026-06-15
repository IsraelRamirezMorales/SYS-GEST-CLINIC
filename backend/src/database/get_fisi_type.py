
from src.database.conection import *
from psycopg2.extras import RealDictCursor

def get_patient_info(id_employees):

    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)


    cur.execute(
                    """
                    SELECT fisio_type FROM employees WHERE id_employees = %s 
                    """,
                    (id_employees,)

                )
    row = cur.fetchone()

    tipo = row["fisio_type"]
   
    cur.close()
    conn.close()

    return tipo