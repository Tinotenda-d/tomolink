from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# SQLAlchemy User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # New fields
    quiz_answers = Column(JSON, nullable=True)   # Stores full quiz answers as JSON (e.g. {"q1": "Aggressive"})
    platform = Column(String, nullable=True)     # e.g. "PC", "Xbox"
    region = Column(String, nullable=True)       # e.g. "EU", "NA"
    games = Column(JSON, nullable=True)          # e.g. ["Valorant", "Overwatch"]

# --------- Pydantic Schemas ---------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class QuizUpdate(BaseModel):
    answers: dict  # e.g. {"q1": "Aggressive", "q2": "Mid-Range"}

class UserEdit(BaseModel):
    platform: Optional[str]
    region: Optional[str]
    games: Optional[List[str]]

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    quiz_answers: Optional[dict] = None
    platform: Optional[str] = None
    region: Optional[str] = None
    games: Optional[List[str]] = None

    class Config:
        from_attributes = True
