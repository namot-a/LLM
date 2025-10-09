"""User model for bot access control."""
from sqlalchemy import Column, String, BigInteger, DateTime, Boolean
from datetime import datetime
from .db import Base


class TelegramUser(Base):
    """Telegram user model for access control."""
    __tablename__ = "telegram_users"
    
    user_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)  # user, admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<TelegramUser(user_id={self.user_id}, username='{self.username}', role='{self.role}')>"

