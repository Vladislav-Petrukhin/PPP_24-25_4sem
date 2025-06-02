from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate, is_admin=False):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    # ОБЯЗАТЕЛЬНО приводим sub к строке
    data = data.copy()
    data["sub"] = str(data["sub"])
    print("create_access_token DATA:", data)  # отладка
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_token(db: Session, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("PAYLOAD:", payload)  # отладка
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return db.query(User).get(int(user_id))
    except JWTError as e:
        print("JWT ERROR:", e)
        return None

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_detail(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def ban_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
    return user

def unban_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = True
        db.commit()
    return user
