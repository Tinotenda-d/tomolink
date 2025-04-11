from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import and_
from app.models.friend import FriendRequest, FriendRequestOut
from app.db.database import get_db
from app.core.auth import get_current_user  # ✅ Make sure it's from core.auth
from app.models.user import User, UserOut

router = APIRouter(prefix="/friends", tags=["friends"])

@router.post("/requests/{user_id}", status_code=status.HTTP_201_CREATED, response_model=FriendRequestOut)
def send_friend_request(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Send a friend request from current_user to the user with id = user_id."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")

    # Check if target user exists
    target_user = db.query(User).get(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if a request already exists between these users
    existing = db.query(FriendRequest).filter(
        or_(
            and_(FriendRequest.from_user_id == current_user.id, FriendRequest.to_user_id == user_id),
            and_(FriendRequest.from_user_id == user_id, FriendRequest.to_user_id == current_user.id)
        )
    ).first()

    if existing:
        if existing.status == "pending":
            raise HTTPException(status_code=400, detail="Friend request already pending between you")
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="You are already friends with this user")

    # Create new friend request
    friend_req = FriendRequest(from_user_id=current_user.id, to_user_id=user_id)
    db.add(friend_req)
    db.commit()
    db.refresh(friend_req)
    return friend_req

@router.get("/requests", response_model=list[FriendRequestOut])
def list_incoming_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List friend requests received by the current user (pending)."""
    requests = db.query(FriendRequest).filter(
        and_(
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending"
        )
    ).all()
    return requests

@router.post("/requests/{request_id}/accept", response_model=FriendRequestOut)
def accept_friend_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Accept a friend request (current user must be the receiver)."""
    friend_req = db.query(FriendRequest).get(request_id)
    if not friend_req:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if friend_req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    if friend_req.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is not pending")

    friend_req.status = "accepted"
    db.commit()
    db.refresh(friend_req)
    return friend_req

@router.post("/requests/{request_id}/reject")
def reject_friend_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Reject a friend request (deletes it)."""
    friend_req = db.query(FriendRequest).get(request_id)
    if not friend_req:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if friend_req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    if friend_req.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is not pending or already handled")

    db.delete(friend_req)
    db.commit()
    return {"detail": "Friend request rejected"}

@router.get("", response_model=list[UserOut])
def list_friends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all friends of the current user."""
    accepted_requests = db.query(FriendRequest).filter(
        FriendRequest.status == "accepted",
        or_(
            FriendRequest.from_user_id == current_user.id,
            FriendRequest.to_user_id == current_user.id
        )
    ).all()

    # Extract other user IDs from accepted requests
    friend_ids = []
    for fr in accepted_requests:
        if fr.from_user_id == current_user.id:
            friend_ids.append(fr.to_user_id)
        else:
            friend_ids.append(fr.from_user_id)

    # Query actual User objects
    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    return friends
