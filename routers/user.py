from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserOut, UserEdit, QuizUpdate
from app.db.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=UserOut)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user

@router.put("/profile/edit", response_model=UserOut)
def edit_profile(data: UserEdit, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update the current user's profile fields (platform, region, games, etc.)."""
    # Apply each provided field update
    updates = data.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/profile/quiz", response_model=UserOut)
def update_quiz_answers(quiz: QuizUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Save or update the current user's quiz answers (onboarding questionnaire)."""
    current_user.quiz_answers = quiz.answers
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete the current user's account (and related data)."""
    db.delete(current_user)
    db.commit()
    return {"detail": "Account deleted"}
