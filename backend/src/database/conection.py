import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def getconection():
    url = os.getenv("DATABASE_URL")
    # If running inside Docker container, map localhost:5433 to db:5432
    if os.path.exists('/.dockerenv') or os.environ.get('IS_DOCKER'):
        if url:
            url = url.replace("@localhost:5433", "@db:5432").replace("@127.0.0.1:5433", "@db:5432")
            # Generic fallback if host port was default
            url = url.replace("@localhost:", "@db:").replace("@127.0.0.1:", "@db:")
    return url
