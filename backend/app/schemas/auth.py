from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = ""

class UserCreate(UserBase):
    password: str
    dob: str | None = None
    phone: str | None = None
    base_currency: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    dob: str | None = None
    phone: str | None = None
    base_currency: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    shabbat_mode: bool
    tz: str
    lat: float
    lon: float

    class Config:
        from_attributes = True
