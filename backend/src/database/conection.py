import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def getconection():
    return os.getenv("DATABASE_URL")
