"""
Batch processing domain models for AriesOne SaaS application.
Implements job management, task processing, and worker coordination.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class JobStatus(str, Enum):
    """Job status types."""
    PENDING = "Pending"
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    PAUSED = "Paused"

class JobPriority(str, Enum):
    """Job priority levels."""
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"

class JobType(str, Enum):
    """Job type categories."""
    BILLING = "Billing"
    INVENTORY = "Inventory"
    REPORT = "Report"
    DATA_PROCESSING = "DataProcessing"

class TaskStatus(str, Enum):
    """Task status types."""
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class WorkerStatus(str, Enum):
    """Worker status types."""
    IDLE = "Idle"
    BUSY = "Busy"
    OFFLINE = "Offline"
    MAINTENANCE = "Maintenance"
    ERROR = "Error"

class BaseJob(Base):
    """
    Abstract base class for all job types.
    Provides common attributes and functionality for job management.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # Job Configuration
    type = Column(SQLEnum(JobType), nullable=False)
    priority = Column(SQLEnum(JobPriority), nullable=False, default=JobPriority.NORMAL)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.PENDING)
    parameters = Column(JSON)
    
    # Scheduling
    scheduled_start = Column(DateTime)
    actual_start = Column(DateTime)
    completed_at = Column(DateTime)
    timeout_minutes = Column(Integer)
    
    # Dependencies
    parent_job_id = Column(Integer, ForeignKey('jobs.id'))
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Results
    result_data = Column(JSON)
    error_details = Column(JSON)
    
    # Metrics
    progress_percent = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    parent_job = relationship("Job", remote_side=[id])
    company = relationship("Company")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])
    tasks = relationship("Task", back_populates="job")

    # Indexes
    __table_args__ = (
        Index('ix_jobs_company_status', 'company_id', 'status'),
        Index('ix_jobs_type_status', 'type', 'status'),
        Index('ix_jobs_scheduled_start', 'scheduled_start'),
    )

class Job(BaseJob):
    """Concrete job implementation."""
    __tablename__ = 'jobs'

    def __repr__(self):
        return f"<Job {self.name} ({self.type})>"

class Task(Base):
    """
    Task model representing individual units of work within a job.
    """
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    worker_id = Column(Integer, ForeignKey('workers.id'))
    name = Column(String(100), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    
    # Task State
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    parameters = Column(JSON)
    result_data = Column(JSON)
    error_details = Column(JSON)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    timeout_minutes = Column(Integer)
    
    # Metrics
    progress_percent = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # System Fields
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="tasks")
    worker = relationship("Worker", back_populates="tasks")

    # Indexes
    __table_args__ = (
        Index('ix_tasks_job_status', 'job_id', 'status'),
        Index('ix_tasks_worker_status', 'worker_id', 'status'),
    )

    def __repr__(self):
        return f"<Task {self.name} (Job: {self.job_id})>"

class Worker(Base):
    """
    Worker model representing processing nodes in the system.
    """
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    host = Column(String(200), nullable=False)
    
    # Worker State
    status = Column(SQLEnum(WorkerStatus), nullable=False, default=WorkerStatus.IDLE)
    is_active = Column(Boolean, nullable=False, default=True)
    last_heartbeat = Column(DateTime)
    
    # Capacity
    max_concurrent_tasks = Column(Integer, nullable=False, default=1)
    current_task_count = Column(Integer, nullable=False, default=0)
    
    # Metrics
    total_tasks_processed = Column(Integer, nullable=False, default=0)
    failed_task_count = Column(Integer, nullable=False, default=0)
    average_task_duration = Column(Integer)  # in seconds
    
    # System Fields
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    tasks = relationship("Task", back_populates="worker")

    # Indexes
    __table_args__ = (
        Index('ix_workers_status', 'status'),
        Index('ix_workers_host', 'host'),
    )

    def __repr__(self):
        return f"<Worker {self.name} ({self.host})>"

class JobHistory(Base):
    """
    Job history model for tracking job state changes.
    """
    __tablename__ = 'job_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    previous_status = Column(SQLEnum(JobStatus))
    new_status = Column(SQLEnum(JobStatus), nullable=False)
    change_reason = Column(String(500))
    
    # Metrics
    progress_percent = Column(Integer)
    error_details = Column(JSON)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    job = relationship("Job")
    created_by = relationship("User")

    # Indexes
    __table_args__ = (
        Index('ix_job_history_job_datetime', 'job_id', 'created_datetime'),
    )

    def __repr__(self):
        return f"<JobHistory {self.job_id} ({self.previous_status} -> {self.new_status})>"

class TaskHistory(Base):
    """
    Task history model for tracking task state changes.
    """
    __tablename__ = 'task_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    previous_status = Column(SQLEnum(TaskStatus))
    new_status = Column(SQLEnum(TaskStatus), nullable=False)
    change_reason = Column(String(500))
    
    # Metrics
    progress_percent = Column(Integer)
    error_details = Column(JSON)
    
    # System Fields
    created_datetime = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    task = relationship("Task")

    # Indexes
    __table_args__ = (
        Index('ix_task_history_task_datetime', 'task_id', 'created_datetime'),
    )

    def __repr__(self):
        return f"<TaskHistory {self.task_id} ({self.previous_status} -> {self.new_status})>"
