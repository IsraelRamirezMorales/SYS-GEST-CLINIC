from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from src.database.conection import getconection


@contextmanager
def get_cursor(dict_rows: bool = True):
    """
    Abre UNA conexión, entrega un cursor y hace commit al salir (rollback si hay error).
    Cada petición debe usar un solo get_cursor() en lugar de abrir varias conexiones.
    """
    conn = psycopg2.connect(getconection())
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor if dict_rows else None)
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()
