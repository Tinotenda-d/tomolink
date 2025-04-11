# app/models/lfg.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class LFGPost(Base):
    __tablename__ = "lfg_posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to User (author). This enables us to join and access user details if needed.
    author = relationship("User")  # refers to User model

# Pydantic schemas
class LFGCreate(BaseModel):
    content: str

class LFGOut(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

