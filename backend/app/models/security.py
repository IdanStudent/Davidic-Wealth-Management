from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..core.db import Base


class UserTwoFA(Base):
    __tablename__ = 'user_twofa'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, index=True, nullable=False)
    secret = Column(String, nullable=True)  # TOTP secret (base32)
    enabled = Column(Boolean, default=False)
    recovery_codes = Column(String, nullable=True)  # comma-separated hashed codes

    user = relationship('User', backref='twofa')

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_twofa_user'),
    )
