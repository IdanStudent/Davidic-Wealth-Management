from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..services.deps import get_current_user
from ..services.jewish import maaser_from_income, get_holidays
from ..models.user import User
from pydantic import BaseModel
from ..utils.security import verify_password, get_password_hash
from ..models.security import UserTwoFA
import secrets
import pyotp
import hashlib

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
        "dob": user.dob,
        "phone": user.phone,
        "base_currency": user.base_currency,
        "address_line1": user.address_line1,
        "address_line2": user.address_line2,
        "city": user.city,
        "state": user.state,
        "postal_code": user.postal_code,
        "country": user.country,
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


class EmailUpdate(BaseModel):
    email: str
    current_password: str


@router.post('/email')
def update_email(payload: EmailUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Invalid password')
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing and existing.id != user.id:
        raise HTTPException(status_code=400, detail='Email already in use')
    user.email = payload.email
    db.add(user)
    db.commit()
    return {"ok": True}


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


@router.post('/password')
def update_password(payload: PasswordUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Invalid current password')
    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)
    db.commit()
    return {"ok": True}


class TwoFAStatus(BaseModel):
    enabled: bool
    secret: str | None = None
    recovery: list[str] | None = None
    provisioning_uri: str | None = None
    qr_b64: str | None = None


@router.get('/2fa', response_model=TwoFAStatus)
def twofa_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rec = db.query(UserTwoFA).filter(UserTwoFA.user_id == user.id).first()
    if not rec:
        return {"enabled": False, "secret": None, "recovery": None, "provisioning_uri": None, "qr_b64": None}
    recovery = rec.recovery_codes.split(',') if rec.recovery_codes else None
    provisioning_uri = None
    qr_b64 = None
    if rec.secret and not rec.enabled:
        totp = pyotp.TOTP(rec.secret)
        provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name="Malka Money")
        try:
            import qrcode
            import io, base64
            img = qrcode.make(provisioning_uri)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            qr_b64 = base64.b64encode(buf.getvalue()).decode()
        except Exception:
            qr_b64 = None
    return {
        "enabled": bool(rec.enabled),
        "secret": rec.secret if not rec.enabled else None,
        "recovery": recovery if not rec.enabled else None,
        "provisioning_uri": provisioning_uri,
        "qr_b64": qr_b64,
    }


class TwoFAEnable(BaseModel):
    enable: bool
    code: str | None = None


@router.post('/2fa')
def twofa_toggle(payload: TwoFAEnable, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rec = db.query(UserTwoFA).filter(UserTwoFA.user_id == user.id).first()
    if not rec:
        rec = UserTwoFA(user_id=user.id)
    if payload.enable:
        # Step 1: if secret doesn't exist, generate secret and recovery codes; keep enabled False until verified
        if not rec.secret:
            rec.secret = pyotp.random_base32()
            codes_plain = [secrets.token_hex(4) for _ in range(5)]
            rec.recovery_codes = ','.join(hashlib.sha256(c.encode()).hexdigest() for c in codes_plain)
            rec.enabled = False
            db.add(rec)
            db.commit()
            # include provisioning uri and qr
            totp = pyotp.TOTP(rec.secret)
            provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name="Malka Money")
            qr_b64 = None
            try:
                import qrcode
                import io, base64
                img = qrcode.make(provisioning_uri)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                qr_b64 = base64.b64encode(buf.getvalue()).decode()
            except Exception:
                pass
            return {"ok": True, "enabled": False, "secret": rec.secret, "recovery_plain": codes_plain, "provisioning_uri": provisioning_uri, "qr_b64": qr_b64}
        # Step 2: if code is provided, verify and enable
        if payload.code:
            totp = pyotp.TOTP(rec.secret)
            code = payload.code.strip().replace(' ', '')
            if not totp.verify(code, valid_window=2):
                raise HTTPException(status_code=400, detail='Invalid 2FA code')
            rec.enabled = True
        else:
            # no code and secret exists: tell client to provide code
            return {"ok": True, "enabled": rec.enabled, "secret": None}
    else:
        rec.enabled = False
    db.add(rec)
    db.commit()
    return {"ok": True, "enabled": rec.enabled}


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
