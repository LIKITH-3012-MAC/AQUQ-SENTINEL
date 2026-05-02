import os
import sys

# Add the directory containing the 'app' module to the path
# If running from root: /Users/likithnaidu/Desktop/AQUQ-SENTINEL
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import engine
from app.models import Base

print("Synchronizing schema (creating missing tables)...")
Base.metadata.create_all(bind=engine)
print("Schema synchronized.")
