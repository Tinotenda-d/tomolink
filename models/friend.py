# app/models/friend.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
from pydantic import BaseModel

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String, default="pending")  # "pending", "accepted"
    # Ensure a unique combination of from->to to avoid duplicate pending requests
    __table_args__ = (UniqueConstraint('from_user_id', 'to_user_id', name='_fr_unique'),)

    # Relationships to load user details if needed
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

# Pydantic schema
class FriendRequestOut(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    status: str

    class Config:
        from_attributes = True

