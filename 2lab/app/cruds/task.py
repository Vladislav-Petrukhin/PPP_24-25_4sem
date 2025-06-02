from sqlalchemy.orm import Session
from app.models.task import ParseTask
from app.schemas.task import TaskCreate
import base64

def create_task(db: Session, task: TaskCreate, user_id: int):
    db_task = ParseTask(
        user_id=user_id,
        url=task.url,
        max_depth=task.max_depth,
        status="pending",
        progress=0
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task_status(db: Session, task_id: int, user_id: int):
    task = db.query(ParseTask).filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return None
    result = None
    if task.status == "completed" and task.result_graphml:
        try:
            result = task.result_graphml.decode("utf-8")
        except Exception:
            result = base64.b64encode(task.result_graphml).decode("utf-8")
    return {
        "status": task.status,
        "progress": task.progress,
        "result": result
    }

def get_all_tasks(db: Session):
    return db.query(ParseTask).all()

def get_task_detail(db: Session, task_id: int):
    return db.query(ParseTask).filter_by(id=task_id).first()
