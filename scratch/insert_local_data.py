import psycopg2
import sys

local_db_url = "postgresql://clinica_user:clinica_password@localhost:5432/clinica_remes"

try:
    print("Connecting to local database...")
    conn = psycopg2.connect(local_db_url)
    cur = conn.cursor()
    
    # 1. Insert patient
    print("Inserting patient Axel...")
    cur.execute(
        """
        INSERT INTO patients (id_patient, name, last_name, phone, amount_to_pay, imp_data, doctor_charge, aseguradora, doctor_sender)
        VALUES (100, 'Axel Local', 'Martínez', '4431234567', 0, 'Notas de prueba', 5, 'GNP', 'Dr. Ortiz')
        ON CONFLICT (id_patient) DO NOTHING;
        """
    )
    
    # 2. Insert session
    print("Inserting session...")
    cur.execute(
        """
        INSERT INTO sesions (id_sesion, entry_date, sesion_type, id_patient, id_employees, entry_time, state)
        VALUES (200, '2026-06-15', 'Consulta', 100, 5, '11:00:00', 'Sin empezar')
        ON CONFLICT (id_sesion) DO NOTHING;
        """
    )
    
    conn.commit()
    print("Data inserted successfully!")
    
    cur.close()
    conn.close()
except Exception as e:
    print("ERROR:", repr(e))
    sys.exit(1)
