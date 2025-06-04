from fastapi import APIRouter, Depends
from app.schemas.user import UserRead
from app.api.deps import get_current_user

router = APIRouter(tags=["users"])

@router.get("/users/me/", response_model=UserRead)
def read_me(current_user = Depends(get_current_user)):
    return current_user
