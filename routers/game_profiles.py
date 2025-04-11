from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.game_profile import GameProfile
from app.models.user import User
from app.db.database import get_db
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/profiles", tags=["game_profiles"])

class GameProfileCreate(BaseModel):
    game_type: str
    playstyle: str
    communication_preference: str
    role_preference: str
    rank: str = None
    additional_preferences: dict = None

class GameProfileOut(GameProfileCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

@router.post("/{game_type}", response_model=GameProfileOut, status_code=status.HTTP_201_CREATED)
def create_game_profile(
    game_type: str,
    profile: GameProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a game profile for the current user."""
    existing_profile = db.query(GameProfile).filter(
        GameProfile.user_id == current_user.id,
        GameProfile.game_type == game_type
    ).first()

    if existing_profile:
        # Update existing profile
        for key, value in profile.dict().items():
            setattr(existing_profile, key, value)
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    else:
        # Create new profile
        new_profile = GameProfile(
            user_id=current_user.id,
            game_type=game_type,
            **profile.dict()
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile

@router.get("/{game_type}", response_model=GameProfileOut)
def get_game_profile(
    game_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's game profile for a specific game."""
    profile = db.query(GameProfile).filter(
        GameProfile.user_id == current_user.id,
        GameProfile.game_type == game_type
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Game profile not found")
    return profile

@router.get("", response_model=List[GameProfileOut])
def list_game_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all game profiles for the current user."""
    return db.query(GameProfile).filter(GameProfile.user_id == current_user.id).all()

@router.delete("/{game_type}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game_profile(
    game_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a game profile for the current user."""
    profile = db.query(GameProfile).filter(
        GameProfile.user_id == current_user.id,
        GameProfile.game_type == game_type
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Game profile not found")
    
    db.delete(profile)
    db.commit()
    return None 