import os
from datetime import datetime, timedelta

import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

# ───── 🔐 CONFIG ──────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "DEV_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# This token URL is used by FastAPI's OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ───── 🔑 TOKEN CREATION ──────────────────────────────────────
def create_access_token(data: dict) -> str:
    """Generate a signed JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ───── 🔐 TOKEN VALIDATION ────────────────────────────────────
def decode_access_token(token: str):
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ───── 🔎 GET CURRENT USER ─────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Extract user from token (used for protected routes)."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload missing")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ───── 🔒 PASSWORD UTILS ───────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plaintext password matches the stored hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
