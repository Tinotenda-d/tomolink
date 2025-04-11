from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class GameProfile(Base):
    __tablename__ = "game_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_type = Column(String, nullable=False)
    playstyle = Column(String, nullable=False)
    communication_preference = Column(String, nullable=False)
    role_preference = Column(String, nullable=False)
    rank = Column(String)
    additional_preferences = Column(JSON)

    user = relationship("User", back_populates="game_profiles") 