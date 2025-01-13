from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, Request
import json

from app.models.access_control import AuditLog, ResourceType
from app.core.config import settings

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    async def log_action(
        self,
        actor_id: int,
        action: str,
        resource_type: ResourceType,
        resource_id: int,
        company_id: int,
        request: Optional[Request] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an action in the audit trail"""
        # Get request information if available
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent")

        # Create audit log entry
        log_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
            company_id=company_id
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_audit_log(
        self,
        log_id: int,
        company_id: int
    ) -> Optional[AuditLog]:
        """Get audit log entry by ID"""
        return self.db.query(AuditLog).filter(
            AuditLog.id == log_id,
            AuditLog.company_id == company_id
        ).first()

    def list_audit_logs(
        self,
        company_id: int,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[int] = None,
        actor_id: Optional[int] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """List audit log entries with filters"""
        query = self.db.query(AuditLog).filter(
            AuditLog.company_id == company_id
        )

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if status:
            query = query.filter(AuditLog.status == status)
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)

        return query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    def get_audit_summary(
        self,
        company_id: int,
        resource_type: Optional[ResourceType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of audit logs"""
        query = self.db.query(AuditLog).filter(
            AuditLog.company_id == company_id
        )

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)

        # Get total count
        total_count = query.count()

        # Get success/failure counts
        success_count = query.filter(AuditLog.status == "success").count()
        failure_count = query.filter(AuditLog.status == "failure").count()

        # Get action counts
        action_counts = {}
        for log in query.all():
            action_counts[log.action] = action_counts.get(log.action, 0) + 1

        # Get top actors
        actor_counts = {}
        for log in query.all():
            actor_counts[log.actor_id] = actor_counts.get(log.actor_id, 0) + 1
        top_actors = sorted(
            actor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_count": total_count,
            "success_count": success_count,
            "failure_count": failure_count,
            "action_counts": action_counts,
            "top_actors": top_actors
        }

    async def cleanup_old_logs(
        self,
        company_id: int,
        retention_days: int = 90
    ) -> int:
        """Clean up old audit logs"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        # Get count of logs to be deleted
        count = self.db.query(AuditLog).filter(
            AuditLog.company_id == company_id,
            AuditLog.timestamp < cutoff_date
        ).count()
        
        # Delete old logs
        self.db.query(AuditLog).filter(
            AuditLog.company_id == company_id,
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        return count

    async def export_audit_logs(
        self,
        company_id: int,
        format: str = "json",
        **filters
    ) -> bytes:
        """Export audit logs in specified format"""
        logs = self.list_audit_logs(company_id, **filters)
        
        if format == "json":
            return self._export_json(logs)
        elif format == "csv":
            return self._export_csv(logs)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(self, logs: List[AuditLog]) -> bytes:
        """Export logs in JSON format"""
        data = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "actor_id": log.actor_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "status": log.status,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            }
            if log.old_values:
                log_dict["old_values"] = log.old_values
            if log.new_values:
                log_dict["new_values"] = log.new_values
            if log.metadata:
                log_dict["metadata"] = log.metadata
            if log.error_message:
                log_dict["error_message"] = log.error_message
            data.append(log_dict)
            
        return json.dumps(data, indent=2).encode()

    def _export_csv(self, logs: List[AuditLog]) -> bytes:
        """Export logs in CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID",
            "Timestamp",
            "Actor ID",
            "Action",
            "Resource Type",
            "Resource ID",
            "Status",
            "IP Address",
            "User Agent",
            "Old Values",
            "New Values",
            "Metadata",
            "Error Message"
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat(),
                log.actor_id,
                log.action,
                log.resource_type,
                log.resource_id,
                log.status,
                log.ip_address,
                log.user_agent,
                json.dumps(log.old_values) if log.old_values else "",
                json.dumps(log.new_values) if log.new_values else "",
                json.dumps(log.metadata) if log.metadata else "",
                log.error_message or ""
            ])
            
        return output.getvalue().encode()
