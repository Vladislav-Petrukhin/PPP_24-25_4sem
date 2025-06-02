from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.session import get_db
from app.cruds.user import get_user_by_token
from app.models.user import User

# Подключаем стандартную схему авторизации
security = HTTPBearer(auto_error=True)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    token = credentials.credentials
    user = get_user_by_token(db, token)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user