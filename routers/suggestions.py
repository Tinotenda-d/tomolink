# app/routers/suggestions.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.models.friend import FriendRequest
from app.db.database import get_db
from app.core.auth import get_current_user
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

# ✅ Response schema for frontend
class SuggestionOut(BaseModel):
    id: int
    username: str
    platform: Optional[str]
    region: Optional[str]
    games: List[str]
    overwatch_role: Optional[str]
    score: int

# ✅ Compatibility scoring logic
def compute_compatibility(current_user: User, candidate: User) -> int:
    score = 0
    current_user_games = current_user.games or []
    candidate_games = candidate.games or []

    if current_user_games and candidate_games:
        shared_games = set(current_user_games) & set(candidate_games)
        score += len(shared_games) * 30
    if current_user.platform and candidate.platform and current_user.platform == candidate.platform:
        score += 20
    if current_user.region and candidate.region and current_user.region == candidate.region:
        score += 20
    if hasattr(candidate, "feedback_score") and candidate.feedback_score:
        score += min(candidate.feedback_score, 100)
    if current_user.quiz_answers and candidate.quiz_answers:
        for key, value in current_user.quiz_answers.items():
            if key in candidate.quiz_answers and candidate.quiz_answers[key] == value:
                score += 5
    if (
        current_user.games and candidate.games and
        "Overwatch" in current_user.games and "Overwatch" in candidate.games and
        current_user.overwatch_role and candidate.overwatch_role and
        current_user.overwatch_role != candidate.overwatch_role
    ):
        score += 10
    return score

# ✅ Suggestion endpoint with filtering + exclusion logic
@router.get("/", response_model=List[SuggestionOut])
def suggest_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    game: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    region: Optional[str] = Query(None)
):
    query = db.query(User).filter(User.id != current_user.id)
    if game:
        query = query.filter(User.games.contains([game]))
    if platform:
        query = query.filter(User.platform == platform)
    if region:
        query = query.filter(User.region == region)

    candidates = query.all()

    exclude_ids = {current_user.id}
    existing_rels = db.query(FriendRequest).filter(
        FriendRequest.status == "accepted",
        or_(FriendRequest.from_user_id == current_user.id, FriendRequest.to_user_id == current_user.id)
    ).all()
    pending_reqs = db.query(FriendRequest).filter(
        FriendRequest.status == "pending",
        or_(FriendRequest.from_user_id == current_user.id, FriendRequest.to_user_id == current_user.id)
    ).all()
    for fr in existing_rels + pending_reqs:
        exclude_ids.add(fr.from_user_id)
        exclude_ids.add(fr.to_user_id)

    results = []
    for user in candidates:
        if user.id in exclude_ids or user.is_private:
            continue
        score = compute_compatibility(current_user, user)
        results.append({
            "id": user.id,
            "username": user.username,
            "platform": user.platform,
            "region": user.region,
            "games": user.games or [],
            "overwatch_role": user.overwatch_role,
            "score": score
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
