import psycopg2
import sys

db_url = "postgresql://neondb_owner:npg_NcEr9l8uwTtz@ep-ancient-waterfall-ah84gpt9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    print("Connecting to Neon database for migration...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # 1. Update Alberca sessions/records (Cristian ID = 9)
    print("Migrating Alberca sessions to Cristian (ID 9)...")
    cur.execute(
        """
        UPDATE sesions 
        SET id_employees = 9 
        WHERE sesion_type = 'Alberca' AND id_employees != 9;
        """
    )
    print(f"Updated {cur.rowcount} rows in sesions.")
    
    cur.execute(
        """
        UPDATE session_records 
        SET id_employees = 9 
        WHERE sesion_type = 'Alberca' AND id_employees != 9;
        """
    )
    print(f"Updated {cur.rowcount} rows in session_records.")

    # 2. Update Terapia sessions/records (Hugo ID = 6 when doctor is Carmen [5])
    print("Migrating Terapia sessions under Carmen to Hugo (ID 6)...")
    cur.execute(
        """
        UPDATE sesions s
        SET id_employees = 6
        FROM patients p
        WHERE s.id_patient = p.id_patient
          AND s.sesion_type = 'Terapia'
          AND p.doctor_charge = 5
          AND s.id_employees != 6;
        """
    )
    print(f"Updated {cur.rowcount} rows in sesions.")
    
    cur.execute(
        """
        UPDATE session_records r
        SET id_employees = 6
        FROM patients p
        WHERE r.id_patient = p.id_patient
          AND r.sesion_type = 'Terapia'
          AND p.doctor_charge = 5
          AND r.id_employees != 6;
        """
    )
    print(f"Updated {cur.rowcount} rows in session_records.")

    # 3. Update Terapia sessions/records (Monica ID = 7 when doctor is Ana [8])
    print("Migrating Terapia sessions under Ana to Monica (ID 7)...")
    cur.execute(
        """
        UPDATE sesions s
        SET id_employees = 7
        FROM patients p
        WHERE s.id_patient = p.id_patient
          AND s.sesion_type = 'Terapia'
          AND p.doctor_charge = 8
          AND s.id_employees != 7;
        """
    )
    print(f"Updated {cur.rowcount} rows in sesions.")
    
    cur.execute(
        """
        UPDATE session_records r
        SET id_employees = 7
        FROM patients p
        WHERE r.id_patient = p.id_patient
          AND r.sesion_type = 'Terapia'
          AND p.doctor_charge = 8
          AND r.id_employees != 7;
        """
    )
    print(f"Updated {cur.rowcount} rows in session_records.")
    
    conn.commit()
    print("Migration completed successfully!")
    
    cur.close()
    conn.close()
except Exception as e:
    print("ERROR running migration:", e)
    sys.exit(1)
