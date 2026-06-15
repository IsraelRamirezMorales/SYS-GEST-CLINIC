
from src.database.id_employee import get_id
from src.database.conection import *
from psycopg2.extras import RealDictCursor
from src.database.get_fisi_type import get_patient_info

def patient_apponintment(id_employees):
   
    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)
    


    tipo_fisio  = get_patient_info(id_employees)
    id_doctor = get_id(id_employees)
    print(tipo_fisio, id_doctor)

    if tipo_fisio == 'Acuática':
        cur.execute(
                    """
                    SELECT p.name,p.last_name,p.phone,p.amount_to_pay,s.entry_date ,s.entry_time, s.state,s.id_sesion,s.sesion_type,p.aseguradora,p.doctor_charge
                    FROM patients p INNER JOIN  sesions s ON s.id_patient = p.id_patient WHERE s.state IN ('Sin empezar', 'Asistió', 'No Asistió')   ORDER BY entry_time ASC 
                    
                    """,
                    
                    
                )
        patients = cur.fetchall()
    
        cur.close()
        conn.close()


    else:
        cur.execute(
                    """
                    SELECT p.name,p.last_name,p.phone,p.amount_to_pay,s.entry_date ,s.entry_time, s.state,s.id_sesion,s.sesion_type,p.aseguradora,p.doctor_charge
                    FROM patients p INNER JOIN  sesions s ON s.id_patient = p.id_patient  WHERE  p.doctor_charge = %s AND s.state IN ('Sin empezar', 'Asistió', 'No Asistió')  ORDER BY entry_time ASC 
                    
                    """,
                    (id_doctor,)
                    
                )
        patients = cur.fetchall()
    
        cur.close()
        conn.close()

            
    return patients
