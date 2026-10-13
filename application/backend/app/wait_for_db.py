import time
import sys
import psycopg
from app.config import settings

def wait_for_database():
    url = settings.database_url.replace("postgresql+psycopg://", "postgresql://")
    print(f"Waiting for database at {url.split('@')[-1]}...")
    
    max_retries = 30
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg.connect(url, connect_timeout=3)
            conn.close()
            print("Database is ready and accepting connections!")
            return 0
        except Exception as e:
            print(f"Attempt {attempt}/{max_retries}: Database not ready yet ({e.__class__.__name__}). Retrying in 1s...")
            time.sleep(1)
            
    print("Database connection timed out after 30 seconds.")
    return 1

if __name__ == "__main__":
    sys.exit(wait_for_database())
