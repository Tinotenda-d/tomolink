from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.game_profile import GameProfile
from app.models.user import User
from app.db.database import get_db
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/matchmaking", tags=["matchmaking"])

class MatchmakingFilters(BaseModel):
    playstyle: str = None
    communication_preference: str = None
    role_preference: str = None
    min_rank: str = None
    max_rank: str = None

class MatchResult(BaseModel):
    user_id: int
    username: str
    game_type: str
    playstyle: str
    communication_preference: str
    role_preference: str
    rank: str
    match_score: float

    class Config:
        from_attributes = True

def calculate_match_score(profile1: GameProfile, profile2: GameProfile) -> float:
    """Calculate a compatibility score between two profiles."""
    score = 0.0
    
    # Playstyle match (30% weight)
    if profile1.playstyle == profile2.playstyle:
        score += 0.3
    
    # Communication preference match (20% weight)
    if profile1.communication_preference == profile2.communication_preference:
        score += 0.2
    
    # Role preference match (30% weight)
    if profile1.role_preference != profile2.role_preference:
        score += 0.3  # Different roles are preferred for team balance
    
    # Rank proximity (20% weight)
    # This is a simplified version - you might want to implement a more sophisticated rank comparison
    if profile1.rank and profile2.rank:
        if profile1.rank == profile2.rank:
            score += 0.2
    
    return score

@router.post("/{game_type}", response_model=List[MatchResult])
def find_matches(
    game_type: str,
    filters: MatchmakingFilters = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find potential matches for the current user based on their game profile and filters."""
    # Get current user's profile
    user_profile = db.query(GameProfile).filter(
        GameProfile.user_id == current_user.id,
        GameProfile.game_type == game_type
    ).first()
    
    if not user_profile:
        raise HTTPException(status_code=404, detail="Game profile not found")
    
    # Query potential matches
    query = db.query(GameProfile, User).join(User).filter(
        GameProfile.game_type == game_type,
        GameProfile.user_id != current_user.id
    )
    
    # Apply filters
    if filters:
        if filters.playstyle:
            query = query.filter(GameProfile.playstyle == filters.playstyle)
        if filters.communication_preference:
            query = query.filter(GameProfile.communication_preference == filters.communication_preference)
        if filters.role_preference:
            query = query.filter(GameProfile.role_preference == filters.role_preference)
        if filters.min_rank:
            query = query.filter(GameProfile.rank >= filters.min_rank)
        if filters.max_rank:
            query = query.filter(GameProfile.rank <= filters.max_rank)
    
    # Get potential matches
    potential_matches = query.all()
    
    # Calculate match scores and format results
    results = []
    for profile, user in potential_matches:
        match_score = calculate_match_score(user_profile, profile)
        results.append(MatchResult(
            user_id=user.id,
            username=user.username,
            game_type=profile.game_type,
            playstyle=profile.playstyle,
            communication_preference=profile.communication_preference,
            role_preference=profile.role_preference,
            rank=profile.rank,
            match_score=match_score
        ))
    
    # Sort by match score (highest first)
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    return results 