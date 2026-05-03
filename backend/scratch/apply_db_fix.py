import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.app.database import engine, SessionLocal
from backend.app.models_ai import Base
from backend.app.db_fixer import fix_database_schema

def run_fix():
    print("--- AquaSentinel DB Hot-Fix Initiated ---")
    
    # 1. Ensure all tables exist
    print("Verifying base tables...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Run the hot-fixer for missing columns
    print("Applying schema hot-fixes...")
    fix_database_schema()
    
    print("--- Hot-Fix Sequence Complete ---")

if __name__ == "__main__":
    run_fix()
