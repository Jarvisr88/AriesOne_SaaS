"""
Database Models Module
This module defines SQLAlchemy models for credential storage.
"""
from sqlalchemy import Column, String, LargeBinary, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CredentialsDB(Base):
    """
    Database model for storing credentials.
    """
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String(50), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
    password_salt = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    class Config:
        """SQLAlchemy model configuration"""
        orm_mode = True
