from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Annotated

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = ""

class UserCreate(UserBase):
    password: Annotated[str, constr(min_length=8, pattern=r'^\S+$')]
    username: Annotated[str, constr(strip_whitespace=True, min_length=3, pattern=r'^\S+$')]
    dob: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    phone: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    base_currency: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    address_line1: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    address_line2: str | None = None
    city: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    state: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    postal_code: Annotated[str, constr(strip_whitespace=True, min_length=1)]
    country: Annotated[str, constr(strip_whitespace=True, min_length=1)]

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[Annotated[str, constr(strip_whitespace=True, min_length=3)]] = None
    password: str
    otp: Optional[str] = None
    recovery: Optional[str] = None

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
