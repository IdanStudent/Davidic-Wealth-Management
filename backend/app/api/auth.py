from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, UserOut, Token
from ..utils.security import verify_password, get_password_hash, create_access_token
from ..models.security import UserTwoFA
from sqlalchemy.exc import OperationalError
import pyotp
import hashlib
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
    # If 2FA is enabled, require otp or recovery in payload when present in schema
    try:
        twofa = db.query(UserTwoFA).filter(UserTwoFA.user_id == user.id, UserTwoFA.enabled == True).first()
    except OperationalError:
        # Legacy DB missing new columns; treat as no 2FA
        twofa = None
    if twofa:
        # Try reading otp or recovery from request body if provided via extra fields
        otp = getattr(user_in, 'otp', None)
        recovery = getattr(user_in, 'recovery', None)
        ok = False
        if otp:
            otp_clean = otp.strip().replace(' ', '')
            ok = pyotp.TOTP(twofa.secret).verify(otp_clean, valid_window=2)
        elif recovery and twofa.recovery_codes:
            hashes = set(twofa.recovery_codes.split(','))
            rh = hashlib.sha256(recovery.encode()).hexdigest()
            if rh in hashes:
                ok = True
                # consume code
                hashes.remove(rh)
                twofa.recovery_codes = ','.join(hashes)
                db.add(twofa)
                db.commit()
        if not ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="2FA required")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
