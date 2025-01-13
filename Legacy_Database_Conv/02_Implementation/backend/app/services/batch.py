"""
Service layer for batch processing operations.
Handles job management, task processing, and worker coordination.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, BackgroundTasks

from ..models.batch import (
    Job, Task, Worker, JobHistory, TaskHistory,
    JobStatus, TaskStatus, WorkerStatus, JobType, JobPriority
)
from ..schemas.batch import (
    JobCreate, JobUpdate, TaskCreate, TaskUpdate,
    WorkerCreate, WorkerUpdate, JobList, TaskList, WorkerList
)
from ..core.security import get_current_user_id
from ..core.config import settings
from ..core.celery_app import celery_app

class BatchService:
    """Service for managing batch processing operations."""

    @staticmethod
    async def create_job(
        db: Session,
        job_data: JobCreate,
        user_id: int
    ) -> Job:
        """Create a new job."""
        job = Job(
            **job_data.model_dump(),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(job)
        db.flush()

        # Create job history entry
        history = JobHistory(
            job_id=job.id,
            new_status=JobStatus.PENDING,
            created_by_id=user_id,
            change_reason="Job created"
        )
        db.add(history)
        db.commit()
        db.refresh(job)
        
        # Trigger job scheduling
        await BatchService._schedule_job(db, job)
        
        return job

    @staticmethod
    async def update_job(
        db: Session,
        job_id: int,
        job_data: JobUpdate,
        user_id: int
    ) -> Job:
        """Update an existing job."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Track status change
        old_status = job.status
        
        # Update job fields
        for field, value in job_data.model_dump(exclude_unset=True).items():
            setattr(job, field, value)
        
        job.last_update_user_id = user_id
        job.last_update_datetime = datetime.now()

        # Create history entry if status changed
        if job_data.status and job_data.status != old_status:
            history = JobHistory(
                job_id=job.id,
                previous_status=old_status,
                new_status=job_data.status,
                created_by_id=user_id,
                change_reason=f"Status updated from {old_status} to {job_data.status}"
            )
            db.add(history)

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: int) -> Job:
        """Get a job by ID."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    @staticmethod
    def list_jobs(
        db: Session,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[JobStatus] = None,
        type: Optional[JobType] = None,
        priority: Optional[JobPriority] = None
    ) -> JobList:
        """List jobs with filtering."""
        query = db.query(Job).filter(Job.company_id == company_id)
        
        if status:
            query = query.filter(Job.status == status)
        if type:
            query = query.filter(Job.type == type)
        if priority:
            query = query.filter(Job.priority == priority)

        total = query.count()
        jobs = query.order_by(desc(Job.created_datetime)).offset(skip).limit(limit).all()
        
        return JobList(
            items=jobs,
            total=total,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def create_task(
        db: Session,
        task_data: TaskCreate
    ) -> Task:
        """Create a new task."""
        task = Task(**task_data.model_dump())
        db.add(task)
        db.flush()

        # Create task history entry
        history = TaskHistory(
            task_id=task.id,
            new_status=TaskStatus.PENDING,
            change_reason="Task created"
        )
        db.add(history)
        db.commit()
        db.refresh(task)
        
        # Trigger task assignment
        await BatchService._assign_task(db, task)
        
        return task

    @staticmethod
    async def update_task(
        db: Session,
        task_id: int,
        task_data: TaskUpdate
    ) -> Task:
        """Update an existing task."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Track status change
        old_status = task.status
        
        # Update task fields
        for field, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        
        task.last_update_datetime = datetime.now()

        # Create history entry if status changed
        if task_data.status and task_data.status != old_status:
            history = TaskHistory(
                task_id=task.id,
                previous_status=old_status,
                new_status=task_data.status,
                change_reason=f"Status updated from {old_status} to {task_data.status}"
            )
            db.add(history)

            # Update job progress if task completed
            if task_data.status == TaskStatus.COMPLETED:
                await BatchService._update_job_progress(db, task.job_id)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task:
        """Get a task by ID."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    @staticmethod
    def list_tasks(
        db: Session,
        job_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> TaskList:
        """List tasks with filtering."""
        query = db.query(Task)
        
        if job_id:
            query = query.filter(Task.job_id == job_id)
        if worker_id:
            query = query.filter(Task.worker_id == worker_id)
        if status:
            query = query.filter(Task.status == status)

        total = query.count()
        tasks = query.order_by(Task.sequence_number).offset(skip).limit(limit).all()
        
        return TaskList(
            items=tasks,
            total=total,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def create_worker(
        db: Session,
        worker_data: WorkerCreate
    ) -> Worker:
        """Create a new worker."""
        worker = Worker(**worker_data.model_dump())
        db.add(worker)
        db.commit()
        db.refresh(worker)
        return worker

    @staticmethod
    async def update_worker(
        db: Session,
        worker_id: int,
        worker_data: WorkerUpdate
    ) -> Worker:
        """Update an existing worker."""
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")

        for field, value in worker_data.model_dump(exclude_unset=True).items():
            setattr(worker, field, value)
        
        worker.last_update_datetime = datetime.now()
        db.commit()
        db.refresh(worker)
        return worker

    @staticmethod
    def get_worker(db: Session, worker_id: int) -> Worker:
        """Get a worker by ID."""
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        return worker

    @staticmethod
    def list_workers(
        db: Session,
        status: Optional[WorkerStatus] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> WorkerList:
        """List workers with filtering."""
        query = db.query(Worker)
        
        if status:
            query = query.filter(Worker.status == status)
        if is_active is not None:
            query = query.filter(Worker.is_active == is_active)

        total = query.count()
        workers = query.order_by(Worker.name).offset(skip).limit(limit).all()
        
        return WorkerList(
            items=workers,
            total=total,
            skip=skip,
            limit=limit
        )

    @staticmethod
    async def _schedule_job(db: Session, job: Job) -> None:
        """Schedule a job for execution."""
        if job.scheduled_start and job.scheduled_start > datetime.now():
            # Schedule for future execution
            celery_app.send_task(
                'schedule_job',
                args=[job.id],
                eta=job.scheduled_start
            )
        else:
            # Start immediately
            job.status = JobStatus.QUEUED
            db.commit()
            
            celery_app.send_task(
                'process_job',
                args=[job.id]
            )

    @staticmethod
    async def _assign_task(db: Session, task: Task) -> None:
        """Assign a task to an available worker."""
        # Find available worker
        worker = db.query(Worker).filter(
            and_(
                Worker.status == WorkerStatus.IDLE,
                Worker.is_active == True,
                Worker.current_task_count < Worker.max_concurrent_tasks
            )
        ).first()

        if worker:
            # Assign task to worker
            task.worker_id = worker.id
            task.status = TaskStatus.ASSIGNED
            worker.current_task_count += 1
            worker.status = WorkerStatus.BUSY
            db.commit()

            # Start task processing
            celery_app.send_task(
                'process_task',
                args=[task.id]
            )

    @staticmethod
    async def _update_job_progress(db: Session, job_id: int) -> None:
        """Update job progress based on completed tasks."""
        # Get job and its tasks
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        tasks = db.query(Task).filter(Task.job_id == job_id).all()
        if not tasks:
            return

        # Calculate progress
        completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
        total_tasks = len(tasks)
        progress = int((completed_tasks / total_tasks) * 100)

        # Update job progress
        job.progress_percent = progress
        
        # Update job status if all tasks completed
        if progress == 100:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()

        db.commit()

    @staticmethod
    def get_job_history(
        db: Session,
        job_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobHistory]:
        """Get history entries for a job."""
        return db.query(JobHistory).filter(
            JobHistory.job_id == job_id
        ).order_by(desc(JobHistory.created_datetime)).offset(skip).limit(limit).all()

    @staticmethod
    def get_task_history(
        db: Session,
        task_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskHistory]:
        """Get history entries for a task."""
        return db.query(TaskHistory).filter(
            TaskHistory.task_id == task_id
        ).order_by(desc(TaskHistory.created_datetime)).offset(skip).limit(limit).all()

    @staticmethod
    async def retry_failed_job(
        db: Session,
        job_id: int,
        user_id: int
    ) -> Job:
        """Retry a failed job."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status != JobStatus.FAILED:
            raise HTTPException(status_code=400, detail="Only failed jobs can be retried")

        if job.retry_count >= job.max_retries:
            raise HTTPException(status_code=400, detail="Maximum retry attempts exceeded")

        # Reset job status
        job.status = JobStatus.PENDING
        job.retry_count += 1
        job.error_details = None
        job.progress_percent = 0
        job.last_update_user_id = user_id
        job.last_update_datetime = datetime.now()

        # Create history entry
        history = JobHistory(
            job_id=job.id,
            previous_status=JobStatus.FAILED,
            new_status=JobStatus.PENDING,
            created_by_id=user_id,
            change_reason=f"Job retry attempt {job.retry_count}"
        )
        db.add(history)

        # Reset tasks
        tasks = db.query(Task).filter(Task.job_id == job_id).all()
        for task in tasks:
            task.status = TaskStatus.PENDING
            task.worker_id = None
            task.started_at = None
            task.completed_at = None
            task.error_details = None
            task.progress_percent = 0

        db.commit()
        db.refresh(job)

        # Reschedule job
        await BatchService._schedule_job(db, job)

        return job

    @staticmethod
    async def cancel_job(
        db: Session,
        job_id: int,
        user_id: int
    ) -> Job:
        """Cancel a job and its tasks."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled")

        # Update job status
        old_status = job.status
        job.status = JobStatus.CANCELLED
        job.last_update_user_id = user_id
        job.last_update_datetime = datetime.now()

        # Create history entry
        history = JobHistory(
            job_id=job.id,
            previous_status=old_status,
            new_status=JobStatus.CANCELLED,
            created_by_id=user_id,
            change_reason="Job cancelled by user"
        )
        db.add(history)

        # Cancel running tasks
        tasks = db.query(Task).filter(
            and_(
                Task.job_id == job_id,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.RUNNING])
            )
        ).all()

        for task in tasks:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()

            # Create task history entry
            task_history = TaskHistory(
                task_id=task.id,
                previous_status=task.status,
                new_status=TaskStatus.CANCELLED,
                change_reason="Task cancelled due to job cancellation"
            )
            db.add(task_history)

        db.commit()
        db.refresh(job)
        return job
