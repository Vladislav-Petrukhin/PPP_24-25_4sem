from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserRead, Token
from app.cruds import user as crud_user
from app.core.security import create_access_token
from app.core.database import get_db

router = APIRouter(tags=["auth"])

@router.post("/sign-up/", response_model=UserRead)
def sign_up(payload: UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud_user.create(db, payload.email, payload.password)
    return user

@router.post("/login/", response_model=Token)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    user = crud_user.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}
