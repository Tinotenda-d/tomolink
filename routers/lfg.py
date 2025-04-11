from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import lfg as lfg_model
from app.models.lfg import LFGPost, LFGCreate, LFGOut
from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/lfg", tags=["lfg"])

@router.post("", response_model=LFGOut, status_code=201)
def create_lfg_post(post: LFGCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new LFG post by the current user."""
    new_post = LFGPost(user_id=current_user.id, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("", response_model=list[LFGOut])
def list_lfg_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all LFG posts (latest first)."""
    posts = db.query(LFGPost).order_by(LFGPost.created_at.desc()).all()
    return posts
