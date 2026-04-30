from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from .. import schemas, models, auth, database, config
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Intelligence identity already exists (Email in use)")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role if user.role in ["user", "researcher", "ngo", "authority"] else "user",
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Auto-login after registration
    access_token = auth.create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "role": db_user.role}
    )
    
    return {
        "success": True,
        "user": db_user,
        "access_token": access_token,
        "role": db_user.role
    }

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials. Access Denied.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended. Contact Command Central.")

    user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return {
        "success": True,
        "user": user,
        "access_token": access_token,
        "role": user.role
    }

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: models.User = Depends(auth.get_current_user)):
    # In a pure JWT system, logout is mostly handled client-side.
    # Optionally, we could blacklist tokens here if we had a Redis store.
    return {"success": True, "message": "Command session terminated successfully"}

@router.patch("/preferences")
def update_preferences(
    prefs: schemas.PreferenceUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if prefs.theme:
        current_user.theme = prefs.theme
    if prefs.language:
        current_user.language = prefs.language
    db.commit()
    return {"success": True, "message": "Neural interface preferences updated"}
