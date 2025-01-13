from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
from pathlib import Path
import shutil
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.services.csv_processor import CSVProcessor, ValidationResult, ProcessingResult
from app.models.core import User, ProcessingJob, ProcessingStatus

router = APIRouter()
csv_processor = CSVProcessor()

def save_upload_file(upload_file: UploadFile) -> Path:
    """Save an uploaded file to the temporary directory."""
    temp_dir = Path(settings.UPLOAD_TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / f"{uuid.uuid4()}_{upload_file.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path

def process_file_background(
    file_path: Path,
    schema_name: str,
    job_id: int,
    db: Session
) -> None:
    """Process a file in the background."""
    try:
        output_dir = Path(settings.PROCESSED_FILES_DIR) / datetime.utcnow().strftime("%Y-%m-%d")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"processed_{file_path.name}"

        # Process the file
        result = csv_processor.process_file(
            str(file_path),
            schema_name,
            str(output_path)
        )

        # Update job status
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job:
            job.status = result.status
            job.processed_rows = result.processed_rows
            job.failed_rows = result.failed_rows
            job.errors = result.errors
            job.output_path = str(output_path) if result.status == ProcessingStatus.COMPLETED else None
            job.end_time = datetime.utcnow()
            db.commit()

    except Exception as e:
        # Update job with error status
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job:
            job.status = ProcessingStatus.FAILED
            job.errors = [{"type": "processing_error", "message": str(e)}]
            job.end_time = datetime.utcnow()
            db.commit()
    finally:
        # Clean up temporary file
        file_path.unlink(missing_ok=True)

@router.get("/schemas")
def list_schemas(
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """List available CSV schemas."""
    return list(csv_processor.schemas.keys())

@router.post("/detect-schema")
async def detect_schema(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Detect the schema of an uploaded CSV file."""
    temp_file = save_upload_file(file)
    try:
        schema_name, confidence = csv_processor.detect_schema(str(temp_file))
        return {
            "detected_schema": schema_name,
            "confidence": confidence
        }
    finally:
        temp_file.unlink(missing_ok=True)

@router.post("/validate")
async def validate_file(
    file: UploadFile = File(...),
    schema_name: str,
    current_user: User = Depends(get_current_user)
) -> ValidationResult:
    """Validate a CSV file against a schema."""
    if schema_name not in csv_processor.schemas:
        raise HTTPException(status_code=400, detail="Invalid schema name")

    temp_file = save_upload_file(file)
    try:
        return csv_processor.validate_file(str(temp_file), schema_name)
    finally:
        temp_file.unlink(missing_ok=True)

@router.post("/process")
async def process_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    schema_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Process a CSV file using the specified schema."""
    if schema_name not in csv_processor.schemas:
        raise HTTPException(status_code=400, detail="Invalid schema name")

    # Save file temporarily
    temp_file = save_upload_file(file)

    # Validate file first
    validation = csv_processor.validate_file(str(temp_file), schema_name)
    if not validation.is_valid:
        temp_file.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail={
                "message": "File validation failed",
                "errors": validation.errors
            }
        )

    # Create processing job
    job = ProcessingJob(
        user_id=current_user.id,
        company_id=current_user.company_id,
        file_name=file.filename,
        schema_name=schema_name,
        status=ProcessingStatus.PENDING,
        start_time=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Start background processing
    background_tasks.add_task(
        process_file_background,
        temp_file,
        schema_name,
        job.id,
        db
    )

    return {
        "job_id": job.id,
        "status": "processing_started",
        "message": "File processing has been started"
    }

@router.get("/jobs")
def list_jobs(
    status: Optional[ProcessingStatus] = None,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ProcessingJob]:
    """List CSV processing jobs."""
    query = db.query(ProcessingJob).filter(
        ProcessingJob.company_id == current_user.company_id
    )
    
    if status:
        query = query.filter(ProcessingJob.status == status)
    
    return query.order_by(ProcessingJob.start_time.desc()).offset(skip).limit(limit).all()

@router.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProcessingJob:
    """Get details of a specific processing job."""
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id,
        ProcessingJob.company_id == current_user.company_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job
