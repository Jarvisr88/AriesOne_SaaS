from typing import Any, Dict, Optional
from datetime import datetime
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

class AuditService:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger('AuditService')

    def log_event(
        self,
        event_type: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event"""
        try:
            session = self.Session()
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.add(audit_log)
            session.commit()
            
            self.logger.info(
                f"Audit log created: {event_type} - {action} on {resource_type}:{resource_id} by {user_id}"
            )
        except Exception as e:
            self.logger.error(f"Failed to create audit log: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """Retrieve audit logs with optional filters"""
        try:
            session = self.Session()
            query = session.query(AuditLog)

            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            if resource_id:
                query = query.filter(AuditLog.resource_id == resource_id)
            if action:
                query = query.filter(AuditLog.action == action)
            if start_time:
                query = query.filter(AuditLog.timestamp >= start_time)
            if end_time:
                query = query.filter(AuditLog.timestamp <= end_time)

            query = query.order_by(AuditLog.timestamp.desc())
            query = query.limit(limit).offset(offset)

            return query.all()
        except Exception as e:
            self.logger.error(f"Failed to retrieve audit logs: {str(e)}")
            raise
        finally:
            session.close()

    def export_audit_logs(
        self,
        start_time: datetime,
        end_time: datetime,
        format: str = 'json'
    ) -> str:
        """Export audit logs in specified format"""
        logs = self.get_audit_logs(start_time=start_time, end_time=end_time, limit=10000)
        
        if format.lower() == 'json':
            return json.dumps([{
                'timestamp': log.timestamp.isoformat(),
                'event_type': log.event_type,
                'user_id': log.user_id,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'action': log.action,
                'details': log.details,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent
            } for log in logs], indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Initialize audit service with database URL from environment
audit_service = AuditService("postgresql://user:password@localhost/audit_db")
