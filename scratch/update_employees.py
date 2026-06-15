import psycopg2
import sys

db_url = "postgresql://neondb_owner:npg_NcEr9l8uwTtz@ep-ancient-waterfall-ah84gpt9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    print("Connecting to database...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Assigning doctor 5 (Carmen) to Hugo (ID 6)...")
    cur.execute("UPDATE employees SET assigned_doctor = 5 WHERE id_employees = 6;")
    
    print("Assigning doctor 8 (Ana Fer) to Monica (ID 7)...")
    cur.execute("UPDATE employees SET assigned_doctor = 8 WHERE id_employees = 7;")
    
    conn.commit()
    print("Database updates completed successfully!")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error during update: {e}", file=sys.stderr)
    sys.exit(1)
