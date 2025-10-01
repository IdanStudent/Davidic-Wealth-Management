from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, UserOut, Token
from ..utils.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name or "",
        dob=user_in.dob or "",
        phone=user_in.phone or "",
        base_currency=user_in.base_currency or "USD",
        address_line1=user_in.address_line1 or "",
        address_line2=user_in.address_line2 or "",
        city=user_in.city or "",
        state=user_in.state or "",
        postal_code=user_in.postal_code or "",
        country=user_in.country or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
