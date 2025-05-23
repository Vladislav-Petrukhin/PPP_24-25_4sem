from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ParseTask(Base):
    __tablename__ = "parse_tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    result = Column(String, nullable=True)
    user_id = Column(Integer)
