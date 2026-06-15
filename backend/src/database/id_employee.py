from src.database.conection import *
from psycopg2.extras import RealDictCursor

def get_id(id_employees):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)


    cur.execute(
                """
                SELECT role FROM employees WHERE id_employees = %s 
                """,
                (id_employees,)
            )
    row = cur.fetchone()

    role = row["role"]
        
    if role == "Fisio":

       cur.execute(
                """
                SELECT assigned_doctor FROM employees WHERE id_employees = %s 
                """,
                (id_employees,)
            )
       row = cur.fetchone()

       id_doctor = row["assigned_doctor"]
       if id_doctor is None:
           id_doctor = id_employees

    else:
       id_doctor = id_employees

    return (id_doctor)