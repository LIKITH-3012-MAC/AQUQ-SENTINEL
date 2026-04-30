from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .. import schemas, auth, database, models
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.AuthStatusResponse)
async def register(user_data: schemas.UserRegister, db: Session = Depends(database.get_db)):
    return await AuthService.register_user(db, user_data)

@router.post("/login", response_model=schemas.Token)
async def login(request: Request, login_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    # Get client info
    ip = request.client.host
    user_agent = request.headers.get("user-agent")
    return await AuthService.authenticate_user(db, login_data, ip, user_agent)

@router.post("/forgot-password/question", response_model=schemas.ForgotQuestionResponse)
async def forgot_password_question(email_data: schemas.ForgotQuestionRequest, db: Session = Depends(database.get_db)):
    return await AuthService.get_security_question(db, email_data)

@router.post("/forgot-password/verify", response_model=schemas.VerifyAnswerResponse)
async def forgot_password_verify(request: Request, verify_data: schemas.VerifyAnswerRequest, db: Session = Depends(database.get_db)):
    ip = request.client.host
    return await AuthService.verify_security_answer(db, verify_data, ip)

@router.post("/forgot-password/reset", response_model=schemas.AuthStatusResponse)
async def forgot_password_reset(reset_data: schemas.ResetPasswordRequest, db: Session = Depends(database.get_db)):
    return await AuthService.reset_password(db, reset_data)

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return current_user

@router.post("/logout", response_model=schemas.AuthStatusResponse)
async def logout(db: Session = Depends(database.get_db), current_user: schemas.UserResponse = Depends(auth.get_current_user)):
    return await AuthService.logout(db, current_user.id)

@router.patch("/preferences")
async def update_preferences(
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
