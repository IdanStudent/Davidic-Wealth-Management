import sys, os

# Ensure 'backend' is on sys.path so 'app' package is importable when executed from repo root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BACKEND = os.path.join(ROOT, 'backend')
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from app.core.db import engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


def clear_2fa(email: str) -> bool:
    with engine.begin() as conn:
        # Lookup user id
        res = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).first()
        if not res:
            print(f"User not found: {email}")
            return False
        user_id = res[0]
        # Attempt delete from user_twofa (if exists)
        try:
            del_res = conn.execute(text("DELETE FROM user_twofa WHERE user_id = :uid"), {"uid": user_id})
        except OperationalError:
            print("TwoFA table not present; nothing to clear.")
            return True
        count = del_res.rowcount if hasattr(del_res, 'rowcount') else 0
        if count:
            print(f"Cleared 2FA for user {email} (id={user_id})")
        else:
            print(f"No 2FA record for user {email} (id={user_id})")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python backend/tools/clear_2fa.py <email>")
        sys.exit(1)
    email = sys.argv[1]
    ok = clear_2fa(email)
    sys.exit(0 if ok else 2)
