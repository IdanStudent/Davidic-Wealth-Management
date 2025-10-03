from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.db import Base


class ConnectedAccount(Base):
    __tablename__ = 'connected_accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    provider = Column(String, nullable=False)  # 'google', 'microsoft', 'plaid', etc.
    status = Column(String, default='linked')  # 'linked', 'pending', 'revoked'
    display_name = Column(String, default='')
    external_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', backref='connections')
