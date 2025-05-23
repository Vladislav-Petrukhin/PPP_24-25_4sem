from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt
from app.models.user import User  # Импорт модели пользователя из твоего проекта
from app.core.config import settings  # Импорт настроек

api_key_header = APIKeyHeader(name="Authorization")

async def get_current_user(api_key: str = Security(api_key_header)) -> User:
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = api_key[len("Bearer "):]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Предполагается, что у тебя есть метод получения пользователя по email
    user = await User.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
