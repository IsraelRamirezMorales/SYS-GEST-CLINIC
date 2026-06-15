from src.database.conection import *
from psycopg2.extras import RealDictCursor

def get_collisions(entry_date, entry_time, sesion_type):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # We query for any active sessions with the same date, time, and session type
    cur.execute(
        """
        SELECT p.name, p.last_name, s.sesion_type, s.entry_time
        FROM sesions s
        INNER JOIN patients p ON s.id_patient = p.id_patient
        WHERE s.entry_date = %s AND s.entry_time = %s AND s.sesion_type = %s AND s.state = 'Sin empezar'
        """,
        (entry_date, entry_time, sesion_type)
    )
    collisions = cur.fetchall()
    
    # Convert time objects to strings so they can be JSON-serialized easily
    for collision in collisions:
        if 'entry_time' in collision and collision['entry_time'] is not None:
            collision['entry_time'] = str(collision['entry_time'])
            
    cur.close()
    conn.close()
    return collisions
