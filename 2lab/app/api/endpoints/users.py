from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.cruds.user import create_user, authenticate_user, create_access_token, get_user_by_email
from app.db.session import get_db
from app.dependencies import get_current_user
from datetime import timedelta
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["users"])

@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = create_user(db, user)
    return db_user

@router.post("/login/", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    print("Перед вызовом create_access_token: db_user.id =", db_user.id, type(db_user.id))
    access_token = create_access_token(
        data={"sub": str(db_user.id)},  # обязательно строкой!
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "id": db_user.id,
        "email": db_user.email,
        "token": access_token
    }


@router.get("/users/me/", response_model=UserOut)
def read_users_me(current_user=Depends(get_current_user)):
    return current_user
