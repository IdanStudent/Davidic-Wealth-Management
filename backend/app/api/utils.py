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
    maaser_pct: float | None = None
    maaser_opt_in: bool | None = None

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
        "maaser_pct": user.maaser_pct,
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


class MaaserSettings(BaseModel):
    maaser_pct: float | None = None
    maaser_opt_in: bool | None = None


@router.post('/maaser_settings')
def set_maaser_settings(payload: MaaserSettings, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.maaser_pct is not None:
        user.maaser_pct = float(payload.maaser_pct)
    if payload.maaser_opt_in is not None:
        # maaser_opt_in is stored as shabbat_mode temporarily until a dedicated column; for now we set maaser_pct=0 when opted-out
        if payload.maaser_opt_in is False:
            user.maaser_pct = 0.0
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "maaser_pct": user.maaser_pct}

@router.post("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True}
