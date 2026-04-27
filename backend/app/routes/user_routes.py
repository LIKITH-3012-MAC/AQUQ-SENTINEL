from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models, auth, database

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Additional endpoints (e.g., PUT /api/users/me) can go here
