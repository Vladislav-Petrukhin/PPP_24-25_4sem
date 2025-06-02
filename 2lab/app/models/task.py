from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, LargeBinary
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime

class ParseTask(Base):
    __tablename__ = "parse_tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    max_depth = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    result_graphml = Column(LargeBinary)
    error_log = Column(Text)

    user = relationship("User")
