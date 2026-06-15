from src.database.conection import *
from src.utils.security import verify_password, get_password_hash

def confirmation_login(user, password):
    print(user)
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id_employees, username, name, role, last_name, password, profile_picture
        FROM employees
        WHERE username = %s
        """,
        (user,)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        id_employees, username, name, role, last_name, db_password, profile_picture = result
        if verify_password(password, db_password):
            # Auto-migrate plain text password to hash
            if not db_password.startswith(("$2a$", "$2b$", "$2y$")):
                try:
                    hashed = get_password_hash(password)
                    conn = psycopg2.connect(getconection())
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE employees SET password = %s WHERE id_employees = %s",
                        (hashed, id_employees)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                except Exception as e:
                    print("Error migrating legacy password to hash:", e)
            
            return (id_employees, username, name, role, last_name, profile_picture)
            
    return None
