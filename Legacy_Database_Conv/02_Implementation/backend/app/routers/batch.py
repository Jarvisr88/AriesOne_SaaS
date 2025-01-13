"""
API routes for batch processing operations.
Provides endpoints for job management, task processing, and worker coordination.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user_id, get_current_active_user
from ..services.batch import BatchService
from ..schemas.batch import (
    JobCreate, JobUpdate, JobResponse, JobList,
    TaskCreate, TaskUpdate, TaskResponse, TaskList,
    WorkerCreate, WorkerUpdate, WorkerResponse, WorkerList,
    JobHistoryResponse, TaskHistoryResponse,
    JobStatus, TaskStatus, WorkerStatus, JobType, JobPriority
)

router = APIRouter(
    prefix="/api/v1/batch",
    tags=["batch"]
)

# Job Management Routes
@router.post("/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> JobResponse:
    """Create a new job."""
    return await BatchService.create_job(db, job_data, current_user_id)

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> JobResponse:
    """Get job details by ID."""
    return BatchService.get_job(db, job_id)

@router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> JobResponse:
    """Update an existing job."""
    return await BatchService.update_job(db, job_id, job_data, current_user_id)

@router.get("/jobs", response_model=JobList)
async def list_jobs(
    company_id: int,
    status: Optional[JobStatus] = None,
    type: Optional[JobType] = None,
    priority: Optional[JobPriority] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> JobList:
    """List jobs with filtering options."""
    return BatchService.list_jobs(
        db, company_id, skip, limit,
        status=status, type=type, priority=priority
    )

@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> JobResponse:
    """Retry a failed job."""
    return await BatchService.retry_failed_job(db, job_id, current_user_id)

@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> JobResponse:
    """Cancel a running job."""
    return await BatchService.cancel_job(db, job_id, current_user_id)

@router.get("/jobs/{job_id}/history", response_model=List[JobHistoryResponse])
async def get_job_history(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> List[JobHistoryResponse]:
    """Get job history entries."""
    return BatchService.get_job_history(db, job_id, skip, limit)

# Task Management Routes
@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> TaskResponse:
    """Create a new task."""
    return await BatchService.create_task(db, task_data)

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> TaskResponse:
    """Get task details by ID."""
    return BatchService.get_task(db, task_id)

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> TaskResponse:
    """Update an existing task."""
    return await BatchService.update_task(db, task_id, task_data)

@router.get("/tasks", response_model=TaskList)
async def list_tasks(
    job_id: Optional[int] = None,
    worker_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> TaskList:
    """List tasks with filtering options."""
    return BatchService.list_tasks(
        db, job_id=job_id, worker_id=worker_id,
        status=status, skip=skip, limit=limit
    )

@router.get("/tasks/{task_id}/history", response_model=List[TaskHistoryResponse])
async def get_task_history(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> List[TaskHistoryResponse]:
    """Get task history entries."""
    return BatchService.get_task_history(db, task_id, skip, limit)

# Worker Management Routes
@router.post("/workers", response_model=WorkerResponse)
async def create_worker(
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> WorkerResponse:
    """Create a new worker."""
    return await BatchService.create_worker(db, worker_data)

@router.get("/workers/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> WorkerResponse:
    """Get worker details by ID."""
    return BatchService.get_worker(db, worker_id)

@router.put("/workers/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    worker_data: WorkerUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> WorkerResponse:
    """Update an existing worker."""
    return await BatchService.update_worker(db, worker_id, worker_data)

@router.get("/workers", response_model=WorkerList)
async def list_workers(
    status: Optional[WorkerStatus] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: int = Depends(get_current_active_user)
) -> WorkerList:
    """List workers with filtering options."""
    return BatchService.list_workers(
        db, status=status, is_active=is_active,
        skip=skip, limit=limit
    )
