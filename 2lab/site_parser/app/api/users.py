from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserMe
from app.cruds.user import get_user_by_email, create_user, verify_password

router = APIRouter()

api_key_header = APIKeyHeader(name="Authorization")

async def get_current_user(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = api_key[len("Bearer "):]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("/sign-up/", response_model=UserOut)
async def sign_up(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = await create_user(db, user.email, user.password)
    token = jwt.encode({"sub": str(new_user.id)}, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return UserOut(id=new_user.id, email=new_user.email, token=token)

@router.post("/login/", response_model=UserOut)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": str(db_user.id)}, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return UserOut(id=db_user.id, email=db_user.email, token=token)

@router.get("/users/me/", response_model=UserMe)
async def users_me(current_user: User = Depends(get_current_user)):
    return UserMe(id=current_user.id, email=current_user.email)
