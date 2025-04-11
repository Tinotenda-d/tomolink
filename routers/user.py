from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User, UserOut, QuizUpdate, UserEdit
from app.db.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently logged-in user."""
    return current_user

@router.put("/profile/quiz", response_model=UserOut)
def update_quiz_answers(
    quiz: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the current user's full quiz answers (stored as JSON).
    Example: {"q1": "Aggressive", "q2": "Tactical"}
    """
    current_user.quiz_answers = quiz.answers
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/profile/edit", response_model=UserOut)
def edit_profile(
    data: UserEdit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update platform, region, and games for the user.
    """
    if data.platform:
        current_user.platform = data.platform
    if data.region:
        current_user.region = data.region
    if data.games:
        current_user.games = data.games

    db.commit()
    db.refresh(current_user)
    return current_user
