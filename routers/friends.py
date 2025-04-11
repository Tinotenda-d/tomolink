from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, and_
from app.models.friend import FriendRequest, FriendRequestOut, FriendRequestDetail
from app.models.user import User, UserOut
from app.db.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/friends", tags=["friends"])

@router.post("/requests/{user_id}", response_model=FriendRequestOut, status_code=status.HTTP_201_CREATED)
def send_friend_request(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Send a friend request from the current user to another user by ID."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself")
    target_user = db.query(User).get(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check if a friend request or friendship already exists between these users
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
    # Create a new pending friend request
    friend_req = FriendRequest(from_user_id=current_user.id, to_user_id=user_id)
    db.add(friend_req)
    db.commit()
    db.refresh(friend_req)
    return friend_req

@router.get("/requests", response_model=list[FriendRequestDetail])
def list_incoming_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all pending friend requests received by the current user."""
    requests = db.query(FriendRequest)\
                 .options(selectinload(FriendRequest.from_user), selectinload(FriendRequest.to_user))\
                 .filter(FriendRequest.to_user_id == current_user.id, FriendRequest.status == "pending")\
                 .all()
    return requests  # Pydantic will serialize into FriendRequestDetail with nested user info

@router.post("/requests/{request_id}/accept", response_model=FriendRequestOut)
def accept_friend_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Accept a friend request. Current user must be the recipient (to_user)."""
    friend_req = db.query(FriendRequest).get(request_id)
    if not friend_req:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if friend_req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    if friend_req.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is not pending")
    # Mark as accepted
    friend_req.status = "accepted"
    db.commit()
    db.refresh(friend_req)
    return friend_req

@router.post("/requests/{request_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_friend_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Reject (delete) a friend request. Current user must be the recipient."""
    friend_req = db.query(FriendRequest).get(request_id)
    if not friend_req:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if friend_req.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    if friend_req.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is already handled")
    # Delete the friend request
    db.delete(friend_req)
    db.commit()
    return {"detail": "Friend request rejected"}

@router.get("", response_model=list[UserOut])
def list_friends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all friends of the current user (all accepted friend connections)."""
    # Find all accepted friend request records involving the current user
    accepted_rels = db.query(FriendRequest).filter(
        FriendRequest.status == "accepted",
        or_(FriendRequest.from_user_id == current_user.id, FriendRequest.to_user_id == current_user.id)
    ).all()
    # Collect the IDs of the other user in each friendship
    friend_ids = []
    for fr in accepted_rels:
        if fr.from_user_id == current_user.id:
            friend_ids.append(fr.to_user_id)
        else:
            friend_ids.append(fr.from_user_id)
    # Fetch User profiles for all friend IDs
    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    return friends
