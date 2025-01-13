from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class CsvImport(Base):
    """SQLAlchemy model for CSV import records."""
    __tablename__ = "csv_imports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    import_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(String, nullable=True)
    row_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    config = Column(JSON, nullable=False)  # Stores CsvConfig as JSON
    headers = Column(JSON, nullable=True)  # Stores headers as JSON array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    errors = relationship("CsvImportError", back_populates="import_record")


class CsvImportError(Base):
    """SQLAlchemy model for CSV import errors."""
    __tablename__ = "csv_import_errors"

    id = Column(Integer, primary_key=True, index=True)
    import_id = Column(Integer, ForeignKey("csv_imports.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    field_index = Column(Integer, nullable=True)
    raw_data = Column(String, nullable=True)
    error_message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    import_record = relationship("CsvImport", back_populates="errors")
