from src.database.id_employee import get_id
from src.database.conection import *
""" CORREGIDA  """
def add_patient(name,last_name,phone,id_employees,instructions,doctor_selected=None,aseguradora=None,doctor_sender=None
):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    amount_to_pay = 0
    

    
 
    if doctor_selected != None:
       cur.execute(
                """
                SELECT id_employees FROM employees WHERE name = %s 
                """,
                (doctor_selected,)
            )
       row = cur.fetchone()
       doctor_charge = row[0]
    else:
        doctor_charge = get_id(id_employees)


    patient =(name,last_name,phone,amount_to_pay,doctor_charge,instructions or "",aseguradora or "") 

    if any(value is None for value in patient):
     return
    
   
    
    cur.execute(
                """
                INSERT INTO patients (name,last_name,phone,amount_to_pay,doctor_charge,imp_data,aseguradora,doctor_sender) VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s);
                """,
                (name,last_name,phone,amount_to_pay,doctor_charge,instructions or "",aseguradora or "",doctor_sender)
            )
    conn.commit()
    cur.close()
    conn.close()

            
    return 
