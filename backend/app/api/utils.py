from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..services.deps import get_current_user
from ..services.jewish import maaser_from_income, get_holidays
from ..models.user import User
from pydantic import BaseModel

class ProfileUpdate(BaseModel):
    full_name: str | None = None
    dob: str | None = None
    phone: str | None = None
    base_currency: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None

router = APIRouter()

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "shabbat_mode": user.shabbat_mode,
        "tz": user.tz,
        "lat": user.lat,
        "lon": user.lon,
    }

@router.get("/maaser")
def maaser(amount: float):
    return {"amount": amount, "maaser": maaser_from_income(amount)}

@router.get("/holidays")
def holidays(year: int):
    return get_holidays(year)

@router.post("/settings")
def update_settings(shabbat_mode: bool, lat: float, lon: float, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.shabbat_mode = bool(shabbat_mode)
    user.lat = float(lat)
    user.lon = float(lon)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True}

@router.post("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True}
