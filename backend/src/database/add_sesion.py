
from src.database.id_employee import get_id
from src.database.conection import *
""" BIEN """
def add_sesions(id_patient,entry_time,entry_date,sesion_type,id_employees):

    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    state = 'Sin empezar'
    

    if sesion_type == 'Consulta':
        amount_to_pay = 800
    elif sesion_type == 'Terapia':
        amount_to_pay = 350
    else:
        amount_to_pay = 400

    cur.execute(
                """
                SELECT doctor_charge FROM patients WHERE id_patient = %s 
                """,
                (id_patient,)
            )
    row = cur.fetchone()

    id_doctor = row[0]

    # Determine the actual employee performing the session
    performing_employee = id_employees
    if sesion_type == 'Alberca':
        performing_employee = 9  # Cristian
    elif sesion_type == 'Terapia':
        if id_doctor == 5:
            performing_employee = 6  # Hugo
        elif id_doctor == 8:
            performing_employee = 7  # Monica
    elif sesion_type == 'Consulta':
        performing_employee = id_doctor

    sesion =(entry_date,sesion_type,id_patient,performing_employee,entry_time,state ) 

    if any(value is None for value in sesion):
     return
    
   
   
    cur.execute(
                """
                INSERT INTO sesions (
                entry_date,
                sesion_type,
                id_patient,
                id_employees,
                entry_time,
                state
                )
                  VALUES
                (%s,%s,%s,%s,%s,%s)
                RETURNING id_sesion;
                """,
                (sesion)
            )
    id_sesion = cur.fetchone()[0]

    cur.execute(
                """
                INSERT INTO session_records (
                id_sesion,
                entry_date,
                entry_time,
                sesion_type,
                id_patient,
                id_employees,
                state
                )
                  VALUES
                (%s,%s,%s,%s,%s,%s,%s);
                """,
                (id_sesion, entry_date, entry_time, sesion_type, id_patient, performing_employee, state)
            )

    cur.execute(
                """
                UPDATE patients SET amount_to_pay = amount_to_pay + %s WHERE id_patient = %s

                """,
                (amount_to_pay,id_patient)
            )
    conn.commit()
    cur.close()
    conn.close()

            
    return 
