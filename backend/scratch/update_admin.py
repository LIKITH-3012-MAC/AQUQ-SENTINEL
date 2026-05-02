import os
import sys
# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app import models, auth

def update_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.email == "admin@aquasentinel.ai").first()
        if admin:
            admin.password_hash = auth.get_password_hash("Admin@123")
            db.commit()
            print("Admin password updated: Admin@123")
        else:
            print("Admin user NOT found.")
    finally:
        db.close()

if __name__ == "__main__":
    update_admin()
