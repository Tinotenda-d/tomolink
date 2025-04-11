# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.friend import FriendRequest
from app.db.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return real-time statistics for the dashboard."""
    # Total registered users (global stat)
    total_users = db.query(User).count()
    # Total successful matches (friend connections globally)
    total_matches = db.query(FriendRequest).filter(FriendRequest.status == "accepted").count()
    # User's number of friends (accepted friend requests involving current_user)
    friends_count = db.query(FriendRequest).filter(
        FriendRequest.status == "accepted",
        (FriendRequest.from_user_id == current_user.id) | (FriendRequest.to_user_id == current_user.id)
    ).count()
    # Pending friend requests awaiting current user (requests received by the user)
    pending_requests = db.query(FriendRequest).filter(
        FriendRequest.status == "pending",
        FriendRequest.to_user_id == current_user.id
    ).count()
    return {
        "total_users": total_users,
        "total_matches": total_matches,
        "friends_count": friends_count,
        "pending_requests": pending_requests
    }
