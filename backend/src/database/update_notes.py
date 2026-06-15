from src.database.conection import *

def update_note(id_patient,imp_data):
    

    
   
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    cur.execute(
                """
                UPDATE patients
                SET
                imp_data = %s
                
                WHERE id_patient = %s;

                """,
                (imp_data,id_patient)
            )
    conn.commit()
    cur.close()
    conn.close()

            
    return 
