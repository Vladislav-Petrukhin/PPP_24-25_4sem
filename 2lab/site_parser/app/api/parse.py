from fastapi import APIRouter, Depends, HTTPException
from app.schemas.parse import ParseRequest, ParseResponse, ParseStatusResponse
from app.services.tasks import run_parse_task
from app.models.task import ParseTask
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import uuid
from sqlalchemy.future import select
from app.api.users import get_current_user

router = APIRouter()

@router.post("/parse_website", response_model=ParseResponse)
async def parse_website(request: ParseRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    task_id = str(uuid.uuid4())
    celery_task = run_parse_task.apply_async(args=[request.url, request.max_depth, request.format], task_id=task_id)
    new_task = ParseTask(task_id=task_id, status="pending", progress=0, user_id=current_user.id)
    db.add(new_task)
    await db.commit()
    return ParseResponse(task_id=task_id)

@router.get("/parse_status", response_model=ParseStatusResponse)
async def parse_status(task_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(select(ParseTask).where(ParseTask.task_id == task_id, ParseTask.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    from celery.result import AsyncResult
    celery_result = AsyncResult(task_id)
    task.status = celery_result.status
    task.progress = 100 if celery_result.ready() else 0
    if celery_result.ready():
        task.result = celery_result.get()
    await db.commit()
    return ParseStatusResponse(
        status=task.status, progress=task.progress, result=task.result
    )
