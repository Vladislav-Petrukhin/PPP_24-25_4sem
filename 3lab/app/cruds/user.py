from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password

def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create(db: Session, email: str, password: str):
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str):
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
