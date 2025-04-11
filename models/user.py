from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# SQLAlchemy User table model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    # Profile/quiz fields
    quiz_answers = Column(JSON, nullable=True)   # Quiz answers (onboarding)
    platform = Column(String, nullable=True)     # e.g. "PC", "Xbox"
    region = Column(String, nullable=True)       # e.g. "NA", "EU"
    games = Column(JSON, nullable=True)          # e.g. ["Overwatch", "Valorant"]
    is_private = Column(Boolean, default=False)  # Profile visibility
    # Matchmaking feedback fields
    feedback_score = Column(Integer, default=0)
    feedback_count = Column(Integer, default=0)
    overwatch_role = Column(String, nullable=True)  # e.g. "Tank", "DPS", "Support"

    game_profiles = relationship("GameProfile", back_populates="user")

# Pydantic schemas for user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class QuizUpdate(BaseModel):
    answers: dict  # quiz answers key -> value

class UserEdit(BaseModel):
    platform: Optional[str]
    region: Optional[str]
    games: Optional[List[str]]
    is_private: Optional[bool] = False
    overwatch_role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    quiz_answers: Optional[dict] = None
    platform: Optional[str] = None
    region: Optional[str] = None
    games: Optional[List[str]] = None
    is_private: Optional[bool] = False
    overwatch_role: Optional[str] = None
    feedback_score: Optional[int] = 0
    feedback_count: Optional[int] = 0

    class Config:
        from_attributes = True

# New: basic public user info for embedding in other responses
class UserBasic(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
