import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

DATABASE_URL = os.getenv("DATABASE_URL")

def reset_database():
    if not DATABASE_URL:
        print("[ERROR] DATABASE_URL not found. Please check your .env file.")
        return

    print(f"[INFO] Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Disable foreign key checks for dropping
        print("[INFO] Dropping all existing tables to fix schema mismatch...")
        
        # Get all table names
        cur.execute("""
            SELECT tablename FROM pg_catalog.pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cur.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"  - Dropping table: {table_name}")
            cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            
        conn.commit()
        print("[SUCCESS] All tables dropped successfully.")
        
        cur.close()
        conn.close()
        print("[INFO] You can now run 'python main.py' to recreate the tables with the correct UUID schema.")
        
    except Exception as e:
        print(f"[CRITICAL] Failed to reset database: {str(e)}")

if __name__ == "__main__":
    reset_database()
