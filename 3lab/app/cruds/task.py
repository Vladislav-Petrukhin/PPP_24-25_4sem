from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus

def create(db: Session, **kwargs) -> Task:
    task = Task(**kwargs)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update(db: Session, task: Task, **kwargs):
    for k, v in kwargs.items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task

def get(db: Session, task_id: str) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()
