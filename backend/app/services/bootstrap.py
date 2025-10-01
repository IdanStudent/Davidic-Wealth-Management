from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.db import SessionLocal
from ..models.user import User
from ..models.finance import Category, CategoryType


def ensure_bootstrap():
    db: Session = SessionLocal()
    try:
        # Ensure there is at least one user? Not necessary.
        # Ensure default categories for each user upon first usage is tricky; we'll add on-demand.
        pass
    finally:
        db.close()


def ensure_default_categories(db: Session, user_id: int):
    existing = {c.name for c in db.query(Category).filter(Category.user_id == user_id).all()}
    defaults = [
        ("Income", CategoryType.INCOME, True, "coin"),
        ("Tzedakah", CategoryType.EXPENSE, True, "charity"),
        ("Food", CategoryType.EXPENSE, False, "utensils"),
        ("Housing", CategoryType.EXPENSE, False, "home"),
        ("Transport", CategoryType.EXPENSE, False, "car"),
    ]
    created = []
    for name, typ, builtin, icon in defaults:
        if name not in existing:
            c = Category(user_id=user_id, name=name, type=typ, is_builtin=builtin, icon=icon)
            db.add(c)
            created.append(c)
    if created:
        db.commit()


def migrate_sqlite(engine):
    # Add new user columns if they don't exist (SQLite only)
    cols = [
        ("dob", "TEXT"),
        ("phone", "TEXT"),
        ("base_currency", "TEXT"),
        ("address_line1", "TEXT"),
        ("address_line2", "TEXT"),
        ("city", "TEXT"),
        ("state", "TEXT"),
        ("postal_code", "TEXT"),
        ("country", "TEXT"),
    ]
    with engine.connect() as conn:
        for name, typ in cols:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {typ}"))
            except Exception:
                # Column likely already exists
                pass
