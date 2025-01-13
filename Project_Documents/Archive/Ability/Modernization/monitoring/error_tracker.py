"""Error tracking system for Ability module."""
import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.error_models import (
    ErrorLog,
    ErrorLogCreate,
    ErrorLogFilter,
    ErrorSeverity
)


class ErrorTracker:
    """Error tracking system."""
    
    def __init__(
        self,
        session: AsyncSession,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize error tracker.
        
        Args:
            session: Database session
            logger: Optional logger instance
        """
        self.session = session
        self.logger = logger or logging.getLogger(__name__)
    
    async def log_error(
        self,
        error: Exception,
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Log error to database.
        
        Args:
            error: Exception instance
            request: Optional request instance
            user_id: Optional user ID
            company_id: Optional company ID
            metadata: Optional additional data
            
        Returns:
            Error ID
        """
        # Generate error ID
        error_id = uuid4()
        
        # Get error details
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = "".join(
            traceback.format_exception(
                type(error),
                error,
                error.__traceback__
            )
        )
        
        # Get request details if available
        request_data = None
        if request:
            request_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_host": request.client.host,
                "path_params": request.path_params,
                "query_params": dict(request.query_params)
            }
            
            # Add body if available and not too large
            if hasattr(request, "body"):
                body = await request.body()
                if len(body) <= 10000:  # 10KB limit
                    try:
                        request_data["body"] = json.loads(body)
                    except:
                        request_data["body"] = body.decode()
        
        # Determine severity
        severity = ErrorSeverity.ERROR
        if isinstance(error, HTTPException):
            if error.status_code < 500:
                severity = ErrorSeverity.WARNING
        
        # Create error log
        error_log = ErrorLog(
            id=error_id,
            error_type=error_type,
            message=error_message,
            stack_trace=stack_trace,
            severity=severity,
            request_data=request_data,
            user_id=user_id,
            company_id=company_id,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        # Save to database
        self.session.add(error_log)
        await self.session.commit()
        
        # Log to logger
        log_method = (
            self.logger.error
            if severity == ErrorSeverity.ERROR
            else self.logger.warning
        )
        log_method(
            f"Error {error_id}: {error_type} - {error_message}",
            extra={
                "error_id": error_id,
                "error_type": error_type,
                "user_id": user_id,
                "company_id": company_id
            }
        )
        
        return error_id
    
    async def get_error(
        self,
        error_id: UUID
    ) -> Optional[ErrorLog]:
        """Get error log by ID.
        
        Args:
            error_id: Error ID
            
        Returns:
            Error log or None
        """
        result = await self.session.execute(
            select(ErrorLog)
            .where(ErrorLog.id == error_id)
        )
        return result.scalar_one_or_none()
    
    async def list_errors(
        self,
        filters: ErrorLogFilter,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ErrorLog], int]:
        """List error logs with filters.
        
        Args:
            filters: Error log filters
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Tuple of (error logs, total count)
        """
        query = select(ErrorLog)
        conditions = []
        
        if filters.error_type:
            conditions.append(
                ErrorLog.error_type == filters.error_type
            )
        
        if filters.severity:
            conditions.append(
                ErrorLog.severity == filters.severity
            )
        
        if filters.user_id:
            conditions.append(
                ErrorLog.user_id == filters.user_id
            )
        
        if filters.company_id:
            conditions.append(
                ErrorLog.company_id == filters.company_id
            )
        
        if filters.start_date:
            conditions.append(
                ErrorLog.created_at >= filters.start_date
            )
        
        if filters.end_date:
            conditions.append(
                ErrorLog.created_at <= filters.end_date
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(
            func.count()
        ).select_from(query.subquery())
        total = await self.session.execute(count_query)
        total = total.scalar_one()
        
        # Get paginated results
        query = query.order_by(
            ErrorLog.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all(), total
    
    async def get_error_stats(
        self,
        company_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get error statistics.
        
        Args:
            company_id: Optional company ID filter
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dictionary of error statistics
        """
        query = select(
            ErrorLog.error_type,
            ErrorLog.severity,
            func.count().label("count")
        )
        
        conditions = []
        
        if company_id:
            conditions.append(
                ErrorLog.company_id == company_id
            )
        
        if start_date:
            conditions.append(
                ErrorLog.created_at >= start_date
            )
        
        if end_date:
            conditions.append(
                ErrorLog.created_at <= end_date
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.group_by(
            ErrorLog.error_type,
            ErrorLog.severity
        )
        
        result = await self.session.execute(query)
        rows = result.all()
        
        stats = {
            "total_errors": sum(row.count for row in rows),
            "by_type": {},
            "by_severity": {
                severity.value: 0
                for severity in ErrorSeverity
            }
        }
        
        for row in rows:
            # Count by type
            if row.error_type not in stats["by_type"]:
                stats["by_type"][row.error_type] = 0
            stats["by_type"][row.error_type] += row.count
            
            # Count by severity
            stats["by_severity"][row.severity] += row.count
        
        return stats
    
    async def cleanup_old_errors(
        self,
        days: int = 30
    ) -> int:
        """Clean up old error logs.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(func.count())
            .select_from(ErrorLog)
            .where(ErrorLog.created_at < cutoff_date)
        )
        count = result.scalar_one()
        
        if count > 0:
            await self.session.execute(
                delete(ErrorLog)
                .where(ErrorLog.created_at < cutoff_date)
            )
            await self.session.commit()
        
        return count
