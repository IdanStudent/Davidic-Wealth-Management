from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from ..core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, default="")
    dob = Column(String, default="")  # YYYY-MM-DD
    phone = Column(String, default="")
    base_currency = Column(String, default="USD")
    address_line1 = Column(String, default="")
    address_line2 = Column(String, default="")
    city = Column(String, default="")
    state = Column(String, default="")
    postal_code = Column(String, default="")
    country = Column(String, default="")
    shabbat_mode = Column(Boolean, default=True)
    tz = Column(String, default="Asia/Jerusalem")
    lat = Column(Float, default=31.778)
    lon = Column(Float, default=35.235)
    # Maaser percentage (0.10 = 10%) user configurable
    maaser_pct = Column(Float, default=0.10)

    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="owner", cascade="all, delete-orphan")
