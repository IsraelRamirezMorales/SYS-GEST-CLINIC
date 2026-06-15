
from src.database.conection import *
from psycopg2.extras import RealDictCursor
from src.database.id_employee import get_id
from src.database.get_fisi_type import get_patient_info

def patients_list(id_employees):
 try:
    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)

    tipo_fisio = get_patient_info(id_employees)
    id_doctor = get_id(id_employees)
    print(tipo_fisio, id_doctor)

    if tipo_fisio == 'Acuática':
        cur.execute(
                    """
                     SELECT id_patient,name,last_name,phone,doctor_sender,amount_to_pay,doctor_charge,aseguradora FROM patients ORDER BY name ASC
                    
                    """,
                    
                    
                )
        patients = cur.fetchall()
    
        cur.close()
        conn.close()


    else:
      cur.execute(
                  """
                  SELECT id_patient,name,last_name,phone,doctor_sender,amount_to_pay,doctor_charge,aseguradora FROM patients WHERE doctor_charge = %s ORDER BY name ASC
                  
                  """,
                  (id_doctor,)
                  
               )
      patients = cur.fetchall()
      
      cur.close()
      conn.close()

            
    return patients
 except Exception as e:
      print("ERROR patients_list:", e)
 return []

   
    
