from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User, UserOut
from app.db.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("/suggestions", response_model=list[UserOut])
def suggest_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.quiz_answers:
        return []

    all_users = db.query(User).filter(User.id != current_user.id).all()
    suggestions = []

    for user in all_users:
        if not user.quiz_answers:
            continue

        # 🎯 Filter: must match region
        if current_user.region and user.region != current_user.region:
            continue

        # 🎯 Filter: must share at least one game
        if current_user.games and user.games:
            if not set(current_user.games).intersection(set(user.games)):
                continue

        # 🧠 Base score: matching quiz answers
        score = sum(
            1 for key in current_user.quiz_answers
            if key in user.quiz_answers and user.quiz_answers[key] == current_user.quiz_answers[key]
        )

        # 🧠 Add weighted score for shared games
        shared_games = set(current_user.games or []).intersection(set(user.games or []))
        score += len(shared_games) * 2  # 2 points per shared game

        if score > 0:
            suggestions.append((user, score))

    sorted_users = sorted(suggestions, key=lambda x: x[1], reverse=True)
    return [user for user, _ in sorted_users]
