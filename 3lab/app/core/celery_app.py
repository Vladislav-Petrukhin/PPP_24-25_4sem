# app/core/celery_app.py
from celery import Celery

# ← Добавляем эти две строки, чтобы SQLAlchemy зарегистрировал обе таблицы в metadata
import app.models.user
import app.models.task

from .config import settings

celery_app = Celery(
    "site_parser",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.celery_tasks"],
)

celery_app.conf.task_track_started = True
