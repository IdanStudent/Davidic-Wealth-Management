import base64
import os
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from hashlib import sha256

from ..core.config import settings

_fernet: Optional[Fernet] = None

def _derive_key() -> bytes:
    dek = os.getenv("DATA_ENCRYPTION_KEY")
    if dek:
        # Expect a URL-safe base64-encoded key of length 32 bytes when decoded
        try:
            raw = base64.urlsafe_b64decode(dek)
            if len(raw) == 32:
                return base64.urlsafe_b64encode(raw)
        except Exception:
            pass
    # Fallback: derive from SECRET_KEY (dev only). In prod, require DATA_ENCRYPTION_KEY.
    # Use SHA-256 of SECRET_KEY to get 32 bytes and base64-urlsafe encode as required by Fernet.
    h = sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(h)

def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_derive_key())
    return _fernet

def encrypt_str(plaintext: Optional[str]) -> Optional[str]:
    if not plaintext:
        return plaintext
    f = get_fernet()
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")

def decrypt_str(ciphertext: Optional[str]) -> Optional[str]:
    if not ciphertext:
        return ciphertext
    f = get_fernet()
    try:
        data = f.decrypt(ciphertext.encode("utf-8"))
        return data.decode("utf-8")
    except InvalidToken:
        # Backward-compat: value may be stored in plaintext (legacy). Return as-is.
        return ciphertext
    except Exception:
        return None
