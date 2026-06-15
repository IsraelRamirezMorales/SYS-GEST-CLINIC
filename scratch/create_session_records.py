import os
import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_NcEr9l8uwTtz@ep-ancient-waterfall-ah84gpt9-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def migrate():
    print("Connecting to Neon DB...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        print("Creating table session_records...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS session_records (
                id_record SERIAL PRIMARY KEY,
                id_sesion INTEGER REFERENCES sesions(id_sesion) ON DELETE SET NULL,
                entry_date DATE NOT NULL,
                entry_time TIME NOT NULL,
                sesion_type VARCHAR(50) NOT NULL,
                id_patient INTEGER REFERENCES patients(id_patient) ON DELETE SET NULL,
                id_employees INTEGER REFERENCES employees(id_employees) ON DELETE SET NULL,
                state VARCHAR(50) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Copying existing sessions...")
        cur.execute("""
            INSERT INTO session_records (id_sesion, entry_date, entry_time, sesion_type, id_patient, id_employees, state)
            SELECT id_sesion, entry_date, entry_time, sesion_type::TEXT, id_patient, id_employees, state::TEXT
            FROM sesions
            ON CONFLICT DO NOTHING;
        """)
        
        conn.commit()
        print("Migration complete!")
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
