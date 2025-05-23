from sqlalchemy.future import select
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(db, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db, email: str, password: str):
    hashed_pw = pwd_context.hash(password)
    user = User(email=email, hashed_password=hashed_pw)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
