from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from fastapi import Request
import json
import logging

from app.models.core import (
    CoreAuditLog,
    AuditLogType,
    User,
    Tenant,
    Company
)
from app.core.config import settings
from app.schemas.audit import AuditLogFilter, AuditLogSummary

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    async def log_event(
        self,
        tenant_id: int,
        log_type: AuditLogType,
        action: str,
        status: str,
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        request: Optional[Request] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> CoreAuditLog:
        """Log an audit event"""
        try:
            log = CoreAuditLog(
                tenant_id=tenant_id,
                company_id=company_id,
                user_id=user_id,
                log_type=log_type,
                action=action,
                status=status,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                request_id=request.state.request_id if request else None,
                old_values=old_values,
                new_values=new_values,
                metadata=metadata,
                error_message=error_message
            )
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)

            # Log to external logging system if configured
            if settings.EXTERNAL_LOGGING_ENABLED:
                await self._log_to_external_system(log)

            return log
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            # Ensure the error doesn't prevent the main operation
            return None

    async def get_audit_logs(
        self,
        tenant_id: int,
        filters: AuditLogFilter,
        page: int = 1,
        page_size: int = 50
    ) -> List[CoreAuditLog]:
        """Get filtered audit logs"""
        query = self.db.query(CoreAuditLog).filter(
            CoreAuditLog.tenant_id == tenant_id
        )

        # Apply filters
        query = self._apply_filters(query, filters)

        # Apply pagination
        query = query.order_by(CoreAuditLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        return query.all()

    async def get_audit_summary(
        self,
        tenant_id: int,
        start_date: datetime,
        end_date: datetime,
        company_id: Optional[int] = None
    ) -> AuditLogSummary:
        """Get summary of audit logs"""
        query = self.db.query(CoreAuditLog).filter(
            CoreAuditLog.tenant_id == tenant_id,
            CoreAuditLog.created_at.between(start_date, end_date)
        )

        if company_id:
            query = query.filter(CoreAuditLog.company_id == company_id)

        # Get total counts
        total_logs = query.count()
        success_logs = query.filter(CoreAuditLog.status == "success").count()
        failure_logs = query.filter(CoreAuditLog.status == "failure").count()

        # Get counts by type
        type_counts = {}
        for log_type in AuditLogType:
            type_counts[log_type.value] = query.filter(
                CoreAuditLog.log_type == log_type
            ).count()

        # Get most active users
        user_counts = {}
        user_logs = query.filter(CoreAuditLog.user_id.isnot(None))
        for log in user_logs:
            user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1

        # Get top 10 users
        top_users = sorted(
            user_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Get user details
        top_user_details = []
        for user_id, count in top_users:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                top_user_details.append({
                    "user_id": user_id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "action_count": count
                })

        return AuditLogSummary(
            total_logs=total_logs,
            success_logs=success_logs,
            failure_logs=failure_logs,
            type_counts=type_counts,
            top_users=top_user_details,
            period_start=start_date,
            period_end=end_date
        )

    async def get_security_events(
        self,
        tenant_id: int,
        start_date: datetime,
        end_date: datetime,
        company_id: Optional[int] = None
    ) -> List[CoreAuditLog]:
        """Get security-related audit logs"""
        query = self.db.query(CoreAuditLog).filter(
            CoreAuditLog.tenant_id == tenant_id,
            CoreAuditLog.log_type == AuditLogType.SECURITY,
            CoreAuditLog.created_at.between(start_date, end_date)
        )

        if company_id:
            query = query.filter(CoreAuditLog.company_id == company_id)

        return query.order_by(CoreAuditLog.created_at.desc()).all()

    async def get_user_activity(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[CoreAuditLog]:
        """Get audit logs for specific user"""
        return self.db.query(CoreAuditLog).filter(
            CoreAuditLog.user_id == user_id,
            CoreAuditLog.created_at.between(start_date, end_date)
        ).order_by(CoreAuditLog.created_at.desc()).all()

    async def get_resource_history(
        self,
        tenant_id: int,
        resource_type: str,
        resource_id: str
    ) -> List[CoreAuditLog]:
        """Get audit history for specific resource"""
        return self.db.query(CoreAuditLog).filter(
            CoreAuditLog.tenant_id == tenant_id,
            CoreAuditLog.metadata["resource_type"].astext == resource_type,
            CoreAuditLog.metadata["resource_id"].astext == resource_id
        ).order_by(CoreAuditLog.created_at.desc()).all()

    def _apply_filters(
        self,
        query,
        filters: AuditLogFilter
    ):
        """Apply filters to audit log query"""
        if filters.company_id:
            query = query.filter(CoreAuditLog.company_id == filters.company_id)
        
        if filters.user_id:
            query = query.filter(CoreAuditLog.user_id == filters.user_id)
        
        if filters.log_type:
            query = query.filter(CoreAuditLog.log_type == filters.log_type)
        
        if filters.action:
            query = query.filter(CoreAuditLog.action == filters.action)
        
        if filters.status:
            query = query.filter(CoreAuditLog.status == filters.status)
        
        if filters.start_date:
            query = query.filter(CoreAuditLog.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(CoreAuditLog.created_at <= filters.end_date)
        
        if filters.ip_address:
            query = query.filter(CoreAuditLog.ip_address == filters.ip_address)
        
        if filters.search_term:
            search = f"%{filters.search_term}%"
            query = query.filter(or_(
                CoreAuditLog.action.ilike(search),
                CoreAuditLog.error_message.ilike(search),
                CoreAuditLog.metadata.cast(String).ilike(search)
            ))

        return query

    async def _log_to_external_system(self, log: CoreAuditLog) -> None:
        """Log event to external logging system"""
        try:
            # Format log data
            log_data = {
                "timestamp": log.created_at.isoformat(),
                "tenant_id": log.tenant_id,
                "company_id": log.company_id,
                "user_id": log.user_id,
                "type": log.log_type.value,
                "action": log.action,
                "status": log.status,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "request_id": log.request_id,
                "metadata": log.metadata,
                "error_message": log.error_message
            }

            # Add external logging implementation here
            # Examples:
            # - AWS CloudWatch
            # - Elasticsearch
            # - Splunk
            # - Custom logging service
            pass

        except Exception as e:
            logger.error(f"Failed to log to external system: {str(e)}")

    async def cleanup_old_logs(self, retention_days: int) -> int:
        """Clean up audit logs older than retention period"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            result = self.db.query(CoreAuditLog).filter(
                CoreAuditLog.created_at < cutoff_date
            ).delete()
            self.db.commit()
            return result
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {str(e)}")
            self.db.rollback()
            return 0
