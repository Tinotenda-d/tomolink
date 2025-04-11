# app/routers/quiz.py (suggestions with weights)
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.database import get_db
from app.core.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/quiz", tags=["quiz"])

def compute_compatibility(current_user: User, candidate: User) -> int:
    score = 0
    if current_user.games and candidate.games:
        shared = set(current_user.games) & set(candidate.games)
        score += len(shared) * 30
    if current_user.platform == candidate.platform:
        score += 20
    if current_user.region == candidate.region:
        score += 20
    if candidate.feedback_score:
        score += min(candidate.feedback_score, 100)  # scale if needed
    if current_user.quiz_answers and candidate.quiz_answers:
        for key in current_user.quiz_answers:
            if key in candidate.quiz_answers and current_user.quiz_answers[key] == candidate.quiz_answers[key]:
                score += 5
    return score

@router.get("/suggestions", response_model=List[dict])
def suggest_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    game: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
):
    query = db.query(User).filter(User.id != current_user.id)
    if game:
        query = query.filter(User.games.contains([game]))
    if platform:
        query = query.filter(User.platform == platform)
    if region:
        query = query.filter(User.region == region)

    candidates = query.all()
    results = []
    for user in candidates:
        if user.is_private:
            continue
        score = compute_compatibility(current_user, user)
        results.append({
            "id": user.id,
            "username": user.username,
            "platform": user.platform,
            "region": user.region,
            "games": user.games,
            "score": score
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
