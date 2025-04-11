from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import User, UserCreate, UserLogin, UserOut
from app.db.database import get_db
from app.core import auth  # includes hash_password, verify_password, create_access_token, etc.
import re

router = APIRouter(prefix="/auth", tags=["auth"])

# User signup
@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email is already taken
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    # Create new user with hashed password
    hashed_pw = auth.hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login (for Swagger/UI via form data)
@router.post("/login")
def login_form(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 login (form data). Returns JWT token if credentials are valid.
    """
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = auth.create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

# Login (JSON payload for frontend)
@router.post("/login/json")
def login_json(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint that accepts JSON payload.
    Returns JWT token if credentials are valid.
    """
    try:
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user.username):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )
        
        # Validate password length
        if len(user.password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Invalid password format"
            )
            
        db_user = db.query(User).filter(User.username == user.username).first()
        
        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
            
        if not auth.verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect password"
            )
            
        token = auth.create_access_token({"sub": str(db_user.id)})
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during login"
        )

# Get current user (profile) using token
@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(auth.get_current_user)):
    """
    Return the profile of the currently authenticated user.
    """
    return current_user
