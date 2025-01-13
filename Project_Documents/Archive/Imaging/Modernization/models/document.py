"""Document models module."""

from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Document(Base):
    """Document model for storing scanned document metadata."""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    original_filename = Column(String)
    storage_path = Column(String)
    mime_type = Column(String)
    size_bytes = Column(Integer)
    page_count = Column(Integer)
    resolution_dpi = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    metadata = Column(JSON)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentPage(Base):
    """Document page model for storing individual page data."""
    __tablename__ = 'document_pages'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    page_number = Column(Integer)
    storage_path = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    resolution_dpi = Column(Integer)
    quality_score = Column(Float)
    ocr_text = Column(String)
    ocr_confidence = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", backref="pages")

class DocumentProcessingJob(Base):
    """Document processing job model for tracking processing tasks."""
    __tablename__ = 'document_processing_jobs'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    job_type = Column(String)  # 'scan', 'ocr', 'convert', 'optimize'
    status = Column(String)  # 'pending', 'processing', 'completed', 'failed'
    priority = Column(Integer, default=0)
    parameters = Column(JSON)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    progress = Column(Float, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", backref="processing_jobs")

class DocumentQualityCheck(Base):
    """Document quality check model for storing quality assessment results."""
    __tablename__ = 'document_quality_checks'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    page_id = Column(Integer, ForeignKey('document_pages.id'))
    check_type = Column(String)  # 'resolution', 'clarity', 'skew', 'noise'
    score = Column(Float)
    details = Column(JSON)
    passed = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", backref="quality_checks")
    page = relationship("DocumentPage", backref="quality_checks")
