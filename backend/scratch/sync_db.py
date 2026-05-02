import os
import sys
# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from app.models import Base

print("Dropping and recreating all tables to ensure schema matches models...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Schema synchronized.")
