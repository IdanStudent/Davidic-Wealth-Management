from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import os
import base64
import hashlib
import hmac
from ..core.config import settings

ALGO = "pbkdf2_sha256"
ITERATIONS = 260000
SALT_LEN = 16


def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))


def get_password_hash(password: str) -> str:
    salt = os.urandom(SALT_LEN)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{ALGO}${ITERATIONS}${_b64(salt)}${_b64(dk)}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algo, iters_s, salt_s, hash_s = hashed_password.split("$")
        if algo != ALGO:
            return False
        iters = int(iters_s)
        salt = _b64d(salt_s)
        expected = _b64d(hash_s)
        dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        if not token:
            return None
        # tolerate a token value that accidentally includes the scheme prefix
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
