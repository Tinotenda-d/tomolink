# app/routers/auth.py
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserCreate, UserLogin, UserOut
from app.db.database import get_db
from app.core import auth  # handles hashing + JWT

router = APIRouter(prefix="/auth", tags=["auth"])

# ───── SIGNUP ────────────────────────────────────────────────────────
@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    print("➡️ Signup endpoint called")
    print("Received user data:", user)

    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    print("User already exists?", existing_user)

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    try:
        hashed_pw = auth.hash_password(user.password)
        print("🔐 Password hashed successfully")
    except Exception as e:
        print("❌ Hashing failed:", e)
        raise HTTPException(status_code=500, detail="Password hashing failed")

    try:
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("✅ User created:", new_user.username)
    except Exception as db_err:
        print("❌ DB error:", db_err)
        raise HTTPException(status_code=500, detail="User creation failed")

    return new_user


# ───── LOGIN ─────────────────────────────────────────────────────────
# @router.post("/login")
# def login(user: UserLogin, db: Session = Depends(get_db)):
#     print("➡️ Login attempt for user:", user.username)
#
#     db_user = db.query(User).filter(User.username == user.username).first()
#
#     if not db_user:
#         print("❌ User not found")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
#
#     if not auth.verify_password(user.password, db_user.hashed_password):
#         print("❌ Password mismatch")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
#
#     token_data = {"sub": str(db_user.id)}
#     access_token = auth.create_access_token(token_data)
#
#     print("✅ Login successful. Token issued for user:", db_user.username)
#
#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }
@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login via form-data for Swagger OAuth2.
    Also works for frontend JSON logins with a separate JSON-based endpoint if needed.
    """
    db_user = db.query(User).filter(User.username == form_data.username).first()

    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth.create_access_token({"sub": str(db_user.id)})

    return {"access_token": token, "token_type": "bearer"}

@router.post("/login/json")
def login_json(user: UserLogin, db: Session = Depends(get_db)):
    """
    Optional JSON-based login for frontend.
    """
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth.create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}
