from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator

class BatchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"

class BatchType(str, Enum):
    CLAIM_SUBMISSION = "claim_submission"
    ELIGIBILITY_CHECK = "eligibility_check"
    STATUS_CHECK = "status_check"
    BENEFICIARY_LOOKUP = "beneficiary_lookup"

class BatchPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class BatchItem(BaseModel):
    item_id: str = Field(..., description="Unique identifier for the batch item")
    data: Dict[str, Any] = Field(..., description="Item data to be processed")
    status: str = Field(default="pending", description="Processing status of the item")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    result: Optional[Dict[str, Any]] = Field(None, description="Processing result")
    retries: int = Field(default=0, description="Number of retry attempts")
    processed_at: Optional[datetime] = Field(None, description="Timestamp of processing")

class BatchJob(BaseModel):
    batch_id: str = Field(..., description="Unique identifier for the batch job")
    type: BatchType = Field(..., description="Type of batch operation")
    status: BatchStatus = Field(default=BatchStatus.PENDING, description="Overall batch status")
    priority: BatchPriority = Field(default=BatchPriority.MEDIUM, description="Processing priority")
    items: List[BatchItem] = Field(..., description="List of items to process")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Processing start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")
    total_items: int = Field(..., description="Total number of items")
    processed_items: int = Field(default=0, description="Number of processed items")
    failed_items: int = Field(default=0, description="Number of failed items")
    creator_id: str = Field(..., description="ID of user who created the batch")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    concurrent_limit: int = Field(default=10, description="Maximum concurrent processing limit")

    @validator('total_items', pre=True, always=True)
    def set_total_items(cls, v, values):
        if 'items' in values:
            return len(values['items'])
        return v

class BatchProgress(BaseModel):
    batch_id: str = Field(..., description="Batch job identifier")
    status: BatchStatus = Field(..., description="Current batch status")
    total_items: int = Field(..., description="Total number of items")
    processed_items: int = Field(..., description="Number of processed items")
    failed_items: int = Field(..., description="Number of failed items")
    progress_percentage: float = Field(..., description="Processing progress percentage")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated seconds remaining")
    started_at: Optional[datetime] = Field(None, description="Processing start timestamp")
    processing_rate: Optional[float] = Field(None, description="Items processed per second")

class BatchResult(BaseModel):
    batch_id: str = Field(..., description="Batch job identifier")
    status: BatchStatus = Field(..., description="Final batch status")
    total_items: int = Field(..., description="Total number of items")
    successful_items: int = Field(..., description="Number of successfully processed items")
    failed_items: int = Field(..., description="Number of failed items")
    started_at: datetime = Field(..., description="Processing start timestamp")
    completed_at: datetime = Field(..., description="Processing completion timestamp")
    processing_time: float = Field(..., description="Total processing time in seconds")
    results: List[BatchItem] = Field(..., description="Individual item results")
    error_summary: Optional[Dict[str, int]] = Field(None, description="Summary of error types")
