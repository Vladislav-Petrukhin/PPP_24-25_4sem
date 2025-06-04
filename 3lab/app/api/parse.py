from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.parse import ParseRequest, ParseResponse, ParseStatus
from app.api.deps import get_current_user
from app.core.database import get_db
from app.cruds.task import create, get
from app.services.celery_tasks import parse_website_task
from app.models.task import TaskStatus

router = APIRouter(tags=["parse"])

@router.post("/parse_website", response_model=ParseResponse)
def parse_site(
    payload: ParseRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = create(
        db,
        user_id=current_user.id,
        url=str(payload.url),
        max_depth=payload.max_depth,
    )
    parse_website_task.apply_async(args=[task.id])
    return {"task_id": task.id}

@router.get("/parse_status", response_model=ParseStatus)
def parse_status(task_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    task = get(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "status": task.status,
        "progress": task.progress,
        "result": task.result_path,
    }
