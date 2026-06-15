from src.database.conection import *
from psycopg2.extras import RealDictCursor

def get_patient_info(id_patient):
    print(id_patient)
    

    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
                """
                SELECT name,last_name,phone,doctor_sender,amount_to_pay,aseguradora FROM patients WHERE id_patient = %s
                
                """,
                (id_patient,)
                
            )
    
    patients = cur.fetchone()
   
    cur.close()
    conn.close()

            
    return patients
