from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.models.lfg import LFGPost, LFGCreate, LFGOut
from app.models.user import User
from app.db.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/lfg", tags=["lfg"])

@router.post("", response_model=LFGOut, status_code=status.HTTP_201_CREATED)
def create_lfg_post(post: LFGCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new LFG post by the current user."""
    new_post = LFGPost(user_id=current_user.id, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("", response_model=list[LFGOut])
def list_lfg_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all LFG posts (latest first). Requires login."""
    posts = db.query(LFGPost).options(selectinload(LFGPost.author))\
                .order_by(LFGPost.created_at.desc()).all()
    return posts  # Each post will include author info (id and username) in the response

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lfg_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete an LFG post. Only the post owner can delete their post."""
    post = db.query(LFGPost).get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="LFG post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(post)
    db.commit()
    return {"detail": "LFG post deleted"}
