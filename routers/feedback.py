# app/routers/feedback.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.user import User
from app.models.friend import FriendRequest
from app.db.database import get_db
from app.core.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackIn(BaseModel):
    rating: int
    comment: Optional[str] = None

@router.post("/{user_id}", status_code=status.HTTP_200_OK)
def submit_feedback(
    user_id: int,
    feedback: FeedbackIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a matched user (by user_id).
    The rating is 1-5, and an optional comment can be included.
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot give feedback to yourself")
    # Verify target user exists
    target_user = db.query(User).get(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Verify that current_user and target_user are friends (matched)
    friendship = db.query(FriendRequest).filter(
        FriendRequest.status == "accepted",
        or_(
            and_(FriendRequest.from_user_id == current_user.id, FriendRequest.to_user_id == user_id),
            and_(FriendRequest.from_user_id == user_id, FriendRequest.to_user_id == current_user.id)
        )
    ).first()
    if not friendship:
        raise HTTPException(status_code=403, detail="You can only leave feedback for users you have matched with")
    # Validate rating value
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    # Update the target user's feedback_score (incremental average)
    old_score = target_user.feedback_score or 0
    old_count = target_user.feedback_count or 0
    new_count = old_count + 1
    # Scale rating to 0-100 (e.g., 5 -> 100, 4 -> 80, etc.) and compute new average
    scaled_rating = feedback.rating * 20
    new_score = ((old_score * old_count) + scaled_rating) / new_count
    # Cap the feedback_score at 100 maximum
    if new_score > 100:
        new_score = 100
    target_user.feedback_score = int(new_score)
    target_user.feedback_count = new_count
    db.commit()
    return {"detail": "Feedback submitted successfully"}
