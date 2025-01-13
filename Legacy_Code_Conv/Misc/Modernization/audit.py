"""
Audit logging implementation.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy.orm import Session
from .database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON
)


class AuditLog(Base):
    """Audit log database model."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    user = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(String(50))
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(200))


class AuditLogger:
    """Service for audit logging."""

    def __init__(self, db: Session):
        """Initialize logger.
        
        Args:
            db: Database session
        """
        self.db = db

    async def log_event(
        self,
        user: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log audit event.
        
        Args:
            user: Username
            action: Action performed
            resource: Resource type
            resource_id: Resource identifier
            details: Additional details
            request: HTTP request
            
        Raises:
            Exception: If logging fails
        """
        try:
            # Create log entry
            log_entry = AuditLog(
                user=user,
                action=action,
                resource=resource,
                resource_id=resource_id,
                details=details
            )
            
            # Add request info if available
            if request:
                log_entry.ip_address = request.client.host
                log_entry.user_agent = request.headers.get(
                    "user-agent"
                )
                
            # Save to database
            self.db.add(log_entry)
            await self.db.flush()
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Audit logging failed: {str(e)}")

    async def get_logs(
        self,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs.
        
        Args:
            user: Filter by username
            action: Filter by action
            resource: Filter by resource type
            resource_id: Filter by resource ID
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of audit logs
        """
        # Build query
        query = self.db.query(AuditLog)
        
        if user:
            query = query.filter(AuditLog.user == user)
            
        if action:
            query = query.filter(AuditLog.action == action)
            
        if resource:
            query = query.filter(AuditLog.resource == resource)
            
        if resource_id:
            query = query.filter(
                AuditLog.resource_id == resource_id
            )
            
        if start_date:
            query = query.filter(
                AuditLog.timestamp >= start_date
            )
            
        if end_date:
            query = query.filter(
                AuditLog.timestamp <= end_date
            )
            
        # Order by timestamp
        query = query.order_by(AuditLog.timestamp.desc())
        
        # Apply pagination
        return await query.offset(skip).limit(limit).all()

    async def get_user_activity(
        self,
        user: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get user activity summary.
        
        Args:
            user: Username
            start_date: Start date
            end_date: End date
            
        Returns:
            Activity counts by action
        """
        # Build query
        query = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id)
        ).filter(
            AuditLog.user == user
        )
        
        if start_date:
            query = query.filter(
                AuditLog.timestamp >= start_date
            )
            
        if end_date:
            query = query.filter(
                AuditLog.timestamp <= end_date
            )
            
        # Group by action
        query = query.group_by(AuditLog.action)
        
        # Execute query
        results = await query.all()
        
        return {
            action: count
            for action, count in results
        }
