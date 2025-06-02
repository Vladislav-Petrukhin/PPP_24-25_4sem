from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskStatus, TaskOut
from app.cruds.task import create_task, get_task_status
from app.db.session import get_db
from app.dependencies import get_current_user
from app.services.parser import crawl_site  # импорт реального парсера
from app.models.task import ParseTask

router = APIRouter(tags=["tasks"])

def run_parser(db: Session, task_id: int, url: str, max_depth: int):
    graphml = crawl_site(url, max_depth)
    task = db.query(ParseTask).filter_by(id=task_id).first()
    if task:
        task.status = "completed"
        task.progress = 100
        task.result_graphml = graphml.encode("utf-8")
        db.commit()
        db.refresh(task)

@router.post("/parse_website/", response_model=TaskOut)
def parse_website(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_task = create_task(db, task, current_user.id)
    # Запускаем реальный парсер в фоне
    background_tasks.add_task(run_parser, db, db_task.id, task.url, task.max_depth)
    return db_task

@router.get("/parse_status", response_model=TaskStatus)
def parse_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    status_dict = get_task_status(db, task_id, current_user.id)
    if not status_dict:
        raise HTTPException(status_code=404, detail="Task not found")
    return status_dict
