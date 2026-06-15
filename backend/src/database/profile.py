import psycopg2
from src.database.conection import getconection

def update_profile_picture(id_employees: int, profile_picture: str):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE employees
            SET profile_picture = %s
            WHERE id_employees = %s
            """,
            (profile_picture, id_employees)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Error update_profile_picture:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_profile_picture_url(id_employees: int):
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT profile_picture 
            FROM employees 
            WHERE id_employees = %s
            """,
            (id_employees,)
        )
        res = cur.fetchone()
        return res[0] if res else None
    except Exception as e:
        print("Error get_profile_picture_url:", e)
        return None
    finally:
        cur.close()
        conn.close()
