"""
Pydantic schemas for batch processing domain.
Provides request and response validation for batch processing operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, constr

from ..models.batch import JobStatus, JobPriority, JobType, TaskStatus, WorkerStatus

# Base schemas
class JobBase(BaseModel):
    """Base schema for jobs."""
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    type: JobType
    priority: JobPriority = JobPriority.NORMAL
    parameters: Optional[Dict[str, Any]] = None
    scheduled_start: Optional[datetime] = None
    timeout_minutes: Optional[int] = Field(None, ge=1)
    parent_job_id: Optional[int] = None
    company_id: int
    max_retries: Optional[int] = Field(3, ge=0)

    @validator('scheduled_start')
    def scheduled_start_must_be_future(cls, v):
        """Validate scheduled start is in the future."""
        if v and v <= datetime.now():
            raise ValueError('scheduled_start must be in the future')
        return v

class TaskBase(BaseModel):
    """Base schema for tasks."""
    job_id: int
    worker_id: Optional[int] = None
    name: constr(min_length=1, max_length=100)
    sequence_number: int = Field(ge=0)
    parameters: Optional[Dict[str, Any]] = None
    timeout_minutes: Optional[int] = Field(None, ge=1)
    max_retries: Optional[int] = Field(3, ge=0)

class WorkerBase(BaseModel):
    """Base schema for workers."""
    name: constr(min_length=1, max_length=100)
    host: constr(min_length=1, max_length=200)
    max_concurrent_tasks: int = Field(1, ge=1)
    is_active: bool = True

# Create schemas
class JobCreate(JobBase):
    """Schema for creating jobs."""
    pass

class TaskCreate(TaskBase):
    """Schema for creating tasks."""
    pass

class WorkerCreate(WorkerBase):
    """Schema for creating workers."""
    pass

# Update schemas
class JobUpdate(BaseModel):
    """Schema for updating jobs."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    priority: Optional[JobPriority] = None
    parameters: Optional[Dict[str, Any]] = None
    scheduled_start: Optional[datetime] = None
    timeout_minutes: Optional[int] = Field(None, ge=1)
    max_retries: Optional[int] = Field(None, ge=0)
    status: Optional[JobStatus] = None

    @validator('scheduled_start')
    def scheduled_start_must_be_future(cls, v):
        """Validate scheduled start is in the future."""
        if v and v <= datetime.now():
            raise ValueError('scheduled_start must be in the future')
        return v

    @validator('status')
    def validate_status_transition(cls, v, values):
        """Validate job status transitions."""
        if v == JobStatus.COMPLETED and values.get('progress_percent', 100) != 100:
            raise ValueError('Cannot mark job as completed if progress is not 100%')
        return v

class TaskUpdate(BaseModel):
    """Schema for updating tasks."""
    worker_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    timeout_minutes: Optional[int] = Field(None, ge=1)
    max_retries: Optional[int] = Field(None, ge=0)
    status: Optional[TaskStatus] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    result_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None

class WorkerUpdate(BaseModel):
    """Schema for updating workers."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    status: Optional[WorkerStatus] = None
    is_active: Optional[bool] = None
    max_concurrent_tasks: Optional[int] = Field(None, ge=1)

# Response schemas
class JobResponse(JobBase):
    """Schema for job responses."""
    id: int
    status: JobStatus
    actual_start: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    progress_percent: int
    retry_count: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime
    tasks: List['TaskResponse'] = []

    class Config:
        from_attributes = True

class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: int
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    progress_percent: int
    retry_count: int
    created_datetime: datetime
    last_update_datetime: datetime

    class Config:
        from_attributes = True

class WorkerResponse(WorkerBase):
    """Schema for worker responses."""
    id: int
    status: WorkerStatus
    last_heartbeat: Optional[datetime] = None
    current_task_count: int
    total_tasks_processed: int
    failed_task_count: int
    average_task_duration: Optional[int] = None
    created_datetime: datetime
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# History schemas
class JobHistoryResponse(BaseModel):
    """Schema for job history responses."""
    id: int
    job_id: int
    previous_status: Optional[JobStatus] = None
    new_status: JobStatus
    change_reason: Optional[str] = None
    progress_percent: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    created_by_id: int
    created_datetime: datetime

    class Config:
        from_attributes = True

class TaskHistoryResponse(BaseModel):
    """Schema for task history responses."""
    id: int
    task_id: int
    previous_status: Optional[TaskStatus] = None
    new_status: TaskStatus
    change_reason: Optional[str] = None
    progress_percent: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    created_datetime: datetime

    class Config:
        from_attributes = True

# List response schemas
class JobList(BaseModel):
    """Schema for job list responses."""
    items: List[JobResponse]
    total: int
    skip: int
    limit: int

class TaskList(BaseModel):
    """Schema for task list responses."""
    items: List[TaskResponse]
    total: int
    skip: int
    limit: int

class WorkerList(BaseModel):
    """Schema for worker list responses."""
    items: List[WorkerResponse]
    total: int
    skip: int
    limit: int

# Job type specific schemas
class BillingJobParameters(BaseModel):
    """Schema for billing job parameters."""
    billing_date: datetime
    company_id: int
    location_ids: Optional[List[int]] = None
    include_rentals: bool = True
    include_claims: bool = True
    include_statements: bool = True

class InventoryJobParameters(BaseModel):
    """Schema for inventory job parameters."""
    company_id: int
    location_ids: Optional[List[int]] = None
    categories: Optional[List[str]] = None
    update_type: str = Field(..., pattern="^(stock|reorder|reconciliation)$")
    reference_date: datetime

class ReportJobParameters(BaseModel):
    """Schema for report job parameters."""
    report_type: str
    start_date: datetime
    end_date: datetime
    company_id: int
    location_ids: Optional[List[int]] = None
    format: str = Field(..., pattern="^(pdf|excel|csv)$")
    parameters: Optional[Dict[str, Any]] = None

class DataProcessingJobParameters(BaseModel):
    """Schema for data processing job parameters."""
    operation_type: str = Field(..., pattern="^(import|export|reconciliation)$")
    data_type: str
    source: str
    destination: str
    filters: Optional[Dict[str, Any]] = None
    transformation_rules: Optional[Dict[str, Any]] = None

# Update forward references
JobResponse.update_forward_refs()
