import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.event import Event

def publish(user_id: int, task_id: str, payload: dict):
    db: Session = SessionLocal()
    event = Event(user_id=user_id, task_id=task_id, data=json.dumps(payload))
    db.add(event)
    db.commit()
    db.close()
