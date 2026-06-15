import psycopg2
import sys

local_db_url = "postgresql://clinica_user:clinica_password@127.0.0.1:5432/clinica_remes"

try:
    print("Connecting to local database...")
    conn = psycopg2.connect(local_db_url)
    cur = conn.cursor()
    
    print("Adding aseguradora column...")
    cur.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS aseguradora VARCHAR(255) DEFAULT '';")
    
    print("Updating assigned_doctor...")
    cur.execute("UPDATE employees SET assigned_doctor = 5 WHERE id_employees = 6;")
    cur.execute("UPDATE employees SET assigned_doctor = 8 WHERE id_employees = 7;")
    
    conn.commit()
    print("Success!")
    
    cur.close()
    conn.close()
except Exception as e:
    # Print clean representation
    print("ERROR:", repr(e))
    sys.exit(1)
