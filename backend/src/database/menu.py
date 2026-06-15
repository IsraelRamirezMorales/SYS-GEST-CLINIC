from src.database.conection import *

def foto_menu(user,password):
    print(user)
    conn = psycopg2.connect(getconection())
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT 1 FROM employees WHERE username = %s and password = %s)",(user,password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    
    return user