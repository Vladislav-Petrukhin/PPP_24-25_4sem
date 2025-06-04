import datetime, uuid
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TaskStatus(str, Enum):
    queued = "queued"
    started = "started"
    progress = "progress"
    completed = "completed"
    failed = "failed"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    url: Mapped[str] = mapped_column(String)
    max_depth: Mapped[int] = mapped_column(Integer, default=1)

    status: Mapped[str] = mapped_column(String, default=TaskStatus.queued)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    pages_parsed: Mapped[int] = mapped_column(Integer, default=0)
    total_pages: Mapped[int] = mapped_column(Integer, default=0)
    links_found: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    result_path: Mapped[str | None] = mapped_column(String, nullable=True)
