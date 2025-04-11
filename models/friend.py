from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
from pydantic import BaseModel
from app.models.user import UserBasic  # import basic user schema for nested output

# SQLAlchemy model for friend requests
class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String, default="pending")  # "pending" or "accepted"
    __table_args__ = (UniqueConstraint('from_user_id', 'to_user_id', name='_fr_unique'),)

    # Relationships to User model for convenience
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user   = relationship("User", foreign_keys=[to_user_id])

# Basic friend request output schema (IDs and status only)
class FriendRequestOut(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    status: str

    class Config:
        from_attributes = True

# Detailed friend request output with user info (for listing pending requests)
class FriendRequestDetail(BaseModel):
    id: int
    status: str
    from_user: UserBasic
    to_user: UserBasic

    class Config:
        from_attributes = True
