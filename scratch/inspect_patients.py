import psycopg2
import sys

db_url = "postgresql://neondb_owner:npg_NcEr9l8uwTtz@ep-ancient-waterfall-ah84gpt9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    print("Connecting to database...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute("SELECT id_patient, name, last_name, doctor_charge, phone FROM patients;")
    rows = cur.fetchall()
    
    print("\nPATIENT LIST:")
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} {r[2]} | Doctor Charge: {r[3]} | Phone: {r[4]}")
        
    print("\nEMPLOYEES LIST:")
    cur.execute("SELECT id_employees, name, role, fisio_type, assigned_doctor FROM employees;")
    erows = cur.fetchall()
    for er in erows:
        print(f"ID: {er[0]} | Name: {er[1]} | Role: {er[2]} | Type: {er[3]} | Assigned Doctor: {er[4]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
