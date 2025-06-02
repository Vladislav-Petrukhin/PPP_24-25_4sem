from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.cruds.user import get_all_users, ban_user, unban_user, get_user_detail
from app.cruds.task import get_all_tasks, get_task_detail
from app.db.session import get_db
from app.dependencies import get_current_admin

router = APIRouter(tags=["admin"])

@router.get("/users/")
def admin_get_users(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return get_all_users(db)

@router.get("/users/{user_id}/")
def admin_get_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return get_user_detail(db, user_id)

@router.post("/users/{user_id}/ban")
def admin_ban_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return ban_user(db, user_id)

@router.post("/users/{user_id}/unban")
def admin_unban_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return unban_user(db, user_id)

@router.get("/tasks/")
def admin_get_tasks(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return get_all_tasks(db)

@router.get("/tasks/{task_id}/")
def admin_get_task(task_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    task = get_task_detail(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
