import os
from celery import Celery

os.environ.setdefault("C_FORCE_ROOT", "true")
celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)
celery.conf.update(task_track_started=True)
