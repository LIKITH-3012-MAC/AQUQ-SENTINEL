from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import uuid
import secrets
from .. import models, schemas, auth
from ..utils.audit import log_action

class AuthService:
    @staticmethod
    async def register_user(db: Session, user_data: schemas.UserRegister):
        # Normalize email
        email = user_data.email.lower().strip()
        
        # Check if exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already exists. Please login."
            )
            
        # Password policy check
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )
            
        # Create user
        new_user = models.User(
            full_name=user_data.full_name,
            email=email,
            password_hash=auth.get_password_hash(user_data.password),
            security_question=user_data.security_question,
            security_answer_hash=auth.get_password_hash(user_data.security_answer.lower().strip()),
            role="user"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        log_action(db, "register_success", user_id=new_user.id, metadata={"email": email})
        
        return {"success": True, "message": "Account created successfully."}

    @staticmethod
    async def authenticate_user(db: Session, login_data: schemas.UserLogin, ip: str = None, user_agent: str = None):
        email = login_data.email.lower().strip()
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            log_action(db, "login_failed_not_found", metadata={"email": email, "ip": ip})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with this email. Please create account."
            )
            
        if not auth.verify_password(login_data.password, user.password_hash):
            user.failed_login_attempts += 1
            db.commit()
            log_action(db, "login_failed_wrong_password", user_id=user.id, metadata={"ip": ip})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )
            
        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        # Create Access Token
        access_token = auth.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        # Track Session
        session = models.LoginSession(
            user_id=user.id,
            jwt_token_id=str(uuid.uuid4()), # Placeholder for token tracking
            ip_address=ip,
            user_agent=user_agent,
            is_active=True
        )
        db.add(session)
        db.commit()
        
        log_action(db, "login_success", user_id=user.id, metadata={"session_id": str(session.id)})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    async def get_security_question(db: Session, email_data: schemas.ForgotQuestionRequest):
        email = email_data.email.lower().strip()
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this email."
            )
            
        log_action(db, "forgot_password_requested", user_id=user.id)
        
        return {
            "success": True,
            "security_question": user.security_question
        }

    @staticmethod
    async def verify_security_answer(db: Session, verify_data: schemas.VerifyAnswerRequest, ip: str = None):
        email = verify_data.email.lower().strip()
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
             raise HTTPException(status_code=404, detail="User not found.")
             
        if not auth.verify_password(verify_data.security_answer.lower().strip(), user.security_answer_hash):
            log_action(db, "security_answer_failed", user_id=user.id, metadata={"ip": ip})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect security answer."
            )
            
        # Success: Issue short-lived reset token
        reset_token_raw = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Store token hash
        reset_token_entry = models.AuthResetToken(
            user_id=user.id,
            token_hash=auth.get_password_hash(reset_token_raw),
            expires_at=expires_at
        )
        db.add(reset_token_entry)
        
        # Log for audit
        audit = models.PasswordResetAudit(
            user_id=user.id,
            email=email,
            security_question=user.security_question,
            answer_verified=True,
            ip_address=ip
        )
        db.add(audit)
        db.commit()
        
        log_action(db, "security_answer_verified", user_id=user.id)
        
        return {
            "success": True,
            "message": "Answer verified.",
            "reset_token": reset_token_raw
        }

    @staticmethod
    async def reset_password(db: Session, reset_data: schemas.ResetPasswordRequest):
        email = reset_data.email.lower().strip()
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
             raise HTTPException(status_code=404, detail="User not found.")
             
        # Find active reset token for this user
        token_entry = db.query(models.AuthResetToken).filter(
            models.AuthResetToken.user_id == user.id,
            models.AuthResetToken.is_used == False,
            models.AuthResetToken.expires_at > datetime.utcnow()
        ).order_by(models.AuthResetToken.created_at.desc()).first()
        
        if not token_entry or not auth.verify_password(reset_data.reset_token, token_entry.token_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired reset token."
            )
            
        # Update password
        user.password_hash = auth.get_password_hash(reset_data.new_password)
        user.password_changed_at = datetime.utcnow()
        user.failed_login_attempts = 0 # reset on password change
        
        # Mark token used
        token_entry.is_used = True
        
        # Close all active sessions for security
        db.query(models.LoginSession).filter(
            models.LoginSession.user_id == user.id,
            models.LoginSession.is_active == True
        ).update({"is_active": False, "logout_time": datetime.utcnow()})
        
        db.commit()
        
        log_action(db, "password_reset_success", user_id=user.id)
        
        return {
            "success": True,
            "message": "Password updated successfully. Please login."
        }

    @staticmethod
    async def logout(db: Session, user_id: uuid.UUID):
        # Deactivate all active sessions for this user
        db.query(models.LoginSession).filter(
            models.LoginSession.user_id == user_id,
            models.LoginSession.is_active == True
        ).update({"is_active": False, "logout_time": datetime.utcnow()})
        
        db.commit()
        log_action(db, "logout_success", user_id=user_id)
        
        return {"success": True, "message": "Logged out successfully."}
