from src.database.conection import *

def edit_patients_info(id_patient,name,last_name,phone,amount_to_pay,doctor_sender=None):


   
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    cur.execute(
                """
                UPDATE patients
                SET
                name = %s,
                last_name = %s,
                phone = %s,
                amount_to_pay = %s,
                doctor_sender = %s
                WHERE id_patient = %s;

                """,
                (name,last_name,phone,amount_to_pay,doctor_sender,id_patient)
            )
    conn.commit()
    cur.close()
    conn.close()

            
    return 
