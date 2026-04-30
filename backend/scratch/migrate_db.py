import psycopg2
import os
from urllib.parse import urlparse

# Use environment variable for security
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check existing columns
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users'")
    existing_cols = [row[0] for row in cur.fetchall()]
    
    print(f"Existing columns: {existing_cols}")
    
    cols_to_add = {
        "theme": "VARCHAR DEFAULT 'dark'",
        "language": "VARCHAR DEFAULT 'en'",
        "status": "VARCHAR DEFAULT 'active'",
        "preferred_language": "VARCHAR DEFAULT 'en'",
        "last_login": "TIMESTAMP WITH TIME ZONE"
    }
    
    for col, definition in cols_to_add.items():
        if col not in existing_cols:
            print(f"Adding column {col}...")
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
