from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base
from pydantic import BaseModel
from datetime import datetime
from app.models.user import UserBasic

# SQLAlchemy model for LFG posts
class LFGPost(Base):
    __tablename__ = "lfg_posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationship to User (post author)
    author = relationship("User")

# Pydantic schema for creating a new LFG post (input)
class LFGCreate(BaseModel):
    content: str

# Pydantic schema for LFG post output (includes author info)
class LFGOut(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: datetime
    author: UserBasic  # nested author info (id and username)

    class Config:
        from_attributes = True
