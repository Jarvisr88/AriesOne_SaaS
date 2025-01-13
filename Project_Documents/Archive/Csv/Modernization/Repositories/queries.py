"""
Optimized queries for CSV import operations.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..Models.types import ImportStatus, ErrorSeverity
from ..Models.models import CsvImport, CsvImportError

class CsvQueries:
    """Optimized database queries for CSV operations."""
    
    @staticmethod
    async def get_import(
        session: Session,
        import_id: int
    ) -> Optional[CsvImport]:
        """Get import record by ID."""
        query = select(CsvImport).where(CsvImport.id == import_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_recent_imports(
        session: Session,
        limit: int = 10,
        offset: int = 0
    ) -> List[CsvImport]:
        """Get recent import records."""
        query = (
            select(CsvImport)
            .order_by(CsvImport.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_import_errors(
        session: Session,
        import_id: int,
        severity: Optional[ErrorSeverity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CsvImportError]:
        """Get errors for an import."""
        conditions = [CsvImportError.import_id == import_id]
        if severity:
            conditions.append(CsvImportError.severity == severity)

        query = (
            select(CsvImportError)
            .where(and_(*conditions))
            .order_by(CsvImportError.row)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_import_stats(
        session: Session,
        import_id: int
    ) -> Dict[str, Any]:
        """Get statistics for an import."""
        # Get row count and error count
        query = select(
            CsvImport.row_count,
            CsvImport.error_count,
            CsvImport.created_at,
            CsvImport.updated_at,
            func.count(CsvImportError.id).label('error_count')
        ).outerjoin(
            CsvImportError,
            CsvImport.id == CsvImportError.import_id
        ).where(
            CsvImport.id == import_id
        ).group_by(
            CsvImport.id
        )
        
        result = await session.execute(query)
        row = result.first()
        
        if not row:
            return None

        # Get error severity distribution
        severity_query = (
            select(
                CsvImportError.severity,
                func.count(CsvImportError.id).label('count')
            )
            .where(CsvImportError.import_id == import_id)
            .group_by(CsvImportError.severity)
        )
        severity_result = await session.execute(severity_query)
        severity_stats = {
            r.severity: r.count for r in severity_result
        }

        return {
            "row_count": row.row_count,
            "error_count": row.error_count,
            "processing_time": (
                row.updated_at - row.created_at
            ).total_seconds(),
            "error_severity": severity_stats
        }

    @staticmethod
    async def find_old_imports(
        session: Session,
        days: int = 30
    ) -> List[CsvImport]:
        """Find imports older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = (
            select(CsvImport)
            .where(CsvImport.created_at < cutoff_date)
            .where(
                or_(
                    CsvImport.status == ImportStatus.COMPLETED,
                    CsvImport.status == ImportStatus.FAILED,
                    CsvImport.status == ImportStatus.CANCELLED
                )
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_import_summary(
        session: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of imports within date range."""
        conditions = []
        if start_date:
            conditions.append(CsvImport.created_at >= start_date)
        if end_date:
            conditions.append(CsvImport.created_at <= end_date)

        # Get status distribution
        status_query = (
            select(
                CsvImport.status,
                func.count(CsvImport.id).label('count')
            )
            .where(and_(*conditions))
            .group_by(CsvImport.status)
        )
        status_result = await session.execute(status_query)
        status_stats = {
            r.status: r.count for r in status_result
        }

        # Get total rows and errors
        totals_query = select(
            func.sum(CsvImport.row_count).label('total_rows'),
            func.sum(CsvImport.error_count).label('total_errors'),
            func.count(CsvImport.id).label('total_imports')
        ).where(and_(*conditions))
        
        totals_result = await session.execute(totals_query)
        totals = totals_result.first()

        return {
            "total_imports": totals.total_imports,
            "total_rows": totals.total_rows or 0,
            "total_errors": totals.total_errors or 0,
            "status_distribution": status_stats
        }
