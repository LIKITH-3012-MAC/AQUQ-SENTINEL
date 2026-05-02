import os
import sys
# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app import models, auth

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.email == "admin@aquasentinel.ai").first()
        if not admin:
            admin = models.User(
                full_name="Chief Intelligence Officer",
                email="admin@aquasentinel.ai",
                password_hash=auth.get_password_hash("Admin@123"),
                security_question="What is the mission?",
                security_answer_hash=auth.get_password_hash("Protect the oceans"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("Admin user created: admin@aquasentinel.ai / Admin@123")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
