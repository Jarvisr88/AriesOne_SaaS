from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from ..models.database import CsvImport, CsvImportError
from ..models import CsvConfig, ParseError


class CsvRepository:
    """Repository for CSV-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_import(
        self, filename: str, config: CsvConfig, headers: Optional[List[str]] = None
    ) -> CsvImport:
        """Create a new CSV import record."""
        db_import = CsvImport(
            filename=filename,
            status="pending",
            config=config.dict(),
            headers=headers,
        )
        self.db.add(db_import)
        self.db.commit()
        self.db.refresh(db_import)
        return db_import

    def update_import_status(
        self,
        import_id: int,
        status: str,
        row_count: Optional[int] = None,
        error_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> CsvImport:
        """Update the status of a CSV import."""
        db_import = self.db.query(CsvImport).filter(CsvImport.id == import_id).first()
        if db_import:
            db_import.status = status
            db_import.updated_at = datetime.utcnow()
            if row_count is not None:
                db_import.row_count = row_count
            if error_count is not None:
                db_import.error_count = error_count
            if error_message is not None:
                db_import.error_message = error_message
            self.db.commit()
            self.db.refresh(db_import)
        return db_import

    def add_import_error(self, import_id: int, error: ParseError) -> CsvImportError:
        """Add an error record for a CSV import."""
        db_error = CsvImportError(
            import_id=import_id,
            line_number=error.line_number,
            field_index=error.field_index,
            raw_data=error.raw_data,
            error_message=error.error_message,
        )
        self.db.add(db_error)
        self.db.commit()
        self.db.refresh(db_error)
        return db_error

    def get_import(self, import_id: int) -> Optional[CsvImport]:
        """Get a CSV import record by ID."""
        return self.db.query(CsvImport).filter(CsvImport.id == import_id).first()

    def get_import_errors(self, import_id: int) -> List[CsvImportError]:
        """Get all errors for a CSV import."""
        return (
            self.db.query(CsvImportError)
            .filter(CsvImportError.import_id == import_id)
            .order_by(CsvImportError.line_number)
            .all()
        )

    def get_recent_imports(self, limit: int = 10) -> List[CsvImport]:
        """Get recent CSV imports."""
        return (
            self.db.query(CsvImport)
            .order_by(desc(CsvImport.created_at))
            .limit(limit)
            .all()
        )

    def delete_import(self, import_id: int) -> bool:
        """Delete a CSV import and its associated errors."""
        db_import = self.db.query(CsvImport).filter(CsvImport.id == import_id).first()
        if db_import:
            self.db.query(CsvImportError).filter(
                CsvImportError.import_id == import_id
            ).delete()
            self.db.delete(db_import)
            self.db.commit()
            return True
        return False
