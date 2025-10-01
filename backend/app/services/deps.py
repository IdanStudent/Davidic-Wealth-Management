from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..utils.security import decode_token
from ..models.user import User
from ..services.shabbat import is_shabbat_now

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def enforce_shabbat_readonly(user: User = Depends(get_current_user)):
    if user.shabbat_mode and is_shabbat_now(user):
        raise HTTPException(status_code=403, detail="Shabbat mode: write actions disabled")
    return True
