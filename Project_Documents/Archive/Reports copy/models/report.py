"""Report models module."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class Report(Base):
    """Base model for all reports."""
    
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    parameters = Column(JSONB)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="reports")
    executions = relationship("ReportExecution", back_populates="report")

    def __repr__(self):
        return f"<Report(id={self.id}, name={self.name}, category={self.category})>"

class ReportExecution(Base):
    """Model for tracking report executions."""
    
    __tablename__ = 'report_executions'

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    parameters = Column(JSONB)
    result_file = Column(String(255))
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="executions")
    user = relationship("User")

    def __repr__(self):
        return f"<ReportExecution(id={self.id}, report_id={self.report_id}, status={self.status})>"

class ReportTemplate(Base):
    """Model for report templates."""
    
    __tablename__ = 'report_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    template_type = Column(String(50), nullable=False)  # sql, jinja, custom
    content = Column(Text, nullable=False)
    parameters = Column(JSONB)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User")

    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, name={self.name}, type={self.template_type})>"
