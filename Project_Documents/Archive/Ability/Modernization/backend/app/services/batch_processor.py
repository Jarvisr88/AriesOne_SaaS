import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
import aioboto3
from fastapi import BackgroundTasks

from app.models.batch import (
    BatchJob,
    BatchItem,
    BatchStatus,
    BatchProgress,
    BatchResult,
    BatchType,
)
from app.services.mainframe_client import MainframeClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        self.session = aioboto3.Session()
        self.sqs_queue_url = settings.AWS_SQS_QUEUE_URL
        self.s3_bucket = settings.AWS_S3_BUCKET
        self._active_batches: Dict[str, BatchJob] = {}
        self._processing_tasks: Dict[str, asyncio.Task] = {}

    async def submit_batch(self, batch_job: BatchJob) -> str:
        """Submit a new batch job for processing"""
        batch_job.batch_id = str(uuid4())
        
        # Store batch metadata in S3
        async with self.session.client('s3') as s3:
            await s3.put_object(
                Bucket=self.s3_bucket,
                Key=f"batches/{batch_job.batch_id}/metadata.json",
                Body=batch_job.json(),
            )

        # Queue items for processing
        async with self.session.client('sqs') as sqs:
            for item in batch_job.items:
                await sqs.send_message(
                    QueueUrl=self.sqs_queue_url,
                    MessageBody=item.json(),
                    MessageAttributes={
                        'batch_id': {'StringValue': batch_job.batch_id, 'DataType': 'String'},
                        'type': {'StringValue': batch_job.type, 'DataType': 'String'},
                        'priority': {'StringValue': str(batch_job.priority), 'DataType': 'String'},
                    },
                )

        self._active_batches[batch_job.batch_id] = batch_job
        return batch_job.batch_id

    async def process_batch(self, batch_id: str, background_tasks: BackgroundTasks):
        """Start processing a batch job"""
        batch_job = self._active_batches.get(batch_id)
        if not batch_job:
            # Load batch from S3
            async with self.session.client('s3') as s3:
                response = await s3.get_object(
                    Bucket=self.s3_bucket,
                    Key=f"batches/{batch_id}/metadata.json",
                )
                batch_data = await response['Body'].read()
                batch_job = BatchJob.parse_raw(batch_data)
                self._active_batches[batch_id] = batch_job

        batch_job.status = BatchStatus.PROCESSING
        batch_job.started_at = datetime.now()

        # Start processing task
        task = asyncio.create_task(self._process_batch_items(batch_job))
        self._processing_tasks[batch_id] = task
        background_tasks.add_task(self._monitor_batch_progress, batch_id)

    async def _process_batch_items(self, batch_job: BatchJob):
        """Process batch items concurrently with rate limiting"""
        async with MainframeClient() as client:
            semaphore = asyncio.Semaphore(batch_job.concurrent_limit)
            tasks = []

            for item in batch_job.items:
                task = asyncio.create_task(
                    self._process_item(client, batch_job, item, semaphore)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        batch_job.status = (
            BatchStatus.COMPLETED
            if batch_job.failed_items == 0
            else BatchStatus.PARTIALLY_COMPLETED
            if batch_job.processed_items > 0
            else BatchStatus.FAILED
        )
        batch_job.completed_at = datetime.now()

        # Store final results in S3
        async with self.session.client('s3') as s3:
            await s3.put_object(
                Bucket=self.s3_bucket,
                Key=f"batches/{batch_job.batch_id}/results.json",
                Body=BatchResult(
                    batch_id=batch_job.batch_id,
                    status=batch_job.status,
                    total_items=batch_job.total_items,
                    successful_items=batch_job.processed_items - batch_job.failed_items,
                    failed_items=batch_job.failed_items,
                    started_at=batch_job.started_at,
                    completed_at=batch_job.completed_at,
                    processing_time=(batch_job.completed_at - batch_job.started_at).total_seconds(),
                    results=batch_job.items,
                    error_summary=self._generate_error_summary(batch_job.items),
                ).json(),
            )

    async def _process_item(
        self,
        client: MainframeClient,
        batch_job: BatchJob,
        item: BatchItem,
        semaphore: asyncio.Semaphore,
    ):
        """Process a single batch item with retries"""
        async with semaphore:
            for attempt in range(batch_job.max_retries):
                try:
                    item.status = "processing"
                    item.retries = attempt + 1

                    if batch_job.type == BatchType.CLAIM_SUBMISSION:
                        response = await client.submit_claim(item.data)
                    elif batch_job.type == BatchType.ELIGIBILITY_CHECK:
                        response = await client.check_eligibility(
                            item.data["medicare_id"],
                            item.data["service_code"],
                        )
                    elif batch_job.type == BatchType.STATUS_CHECK:
                        response = await client.get_claim_status(item.data["claim_id"])
                    elif batch_job.type == BatchType.BENEFICIARY_LOOKUP:
                        response = await client.get_beneficiary(item.data["medicare_id"])

                    if response.success:
                        item.status = "completed"
                        item.result = response.data
                        item.processed_at = datetime.now()
                        batch_job.processed_items += 1
                        break
                    else:
                        raise Exception(response.error.message)

                except Exception as e:
                    logger.error(
                        f"Error processing item {item.item_id} (attempt {attempt + 1}): {str(e)}"
                    )
                    item.error = str(e)
                    if attempt == batch_job.max_retries - 1:
                        item.status = "failed"
                        batch_job.failed_items += 1
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _monitor_batch_progress(self, batch_id: str):
        """Monitor and update batch processing progress"""
        while True:
            batch_job = self._active_batches.get(batch_id)
            if not batch_job or batch_job.status in [
                BatchStatus.COMPLETED,
                BatchStatus.FAILED,
                BatchStatus.PARTIALLY_COMPLETED,
            ]:
                break

            progress = BatchProgress(
                batch_id=batch_id,
                status=batch_job.status,
                total_items=batch_job.total_items,
                processed_items=batch_job.processed_items,
                failed_items=batch_job.failed_items,
                progress_percentage=(batch_job.processed_items / batch_job.total_items) * 100,
                started_at=batch_job.started_at,
            )

            if batch_job.started_at:
                elapsed_time = (datetime.now() - batch_job.started_at).total_seconds()
                if batch_job.processed_items > 0:
                    progress.processing_rate = batch_job.processed_items / elapsed_time
                    remaining_items = batch_job.total_items - batch_job.processed_items
                    progress.estimated_time_remaining = int(
                        remaining_items / progress.processing_rate
                    )

            # Store progress in S3
            async with self.session.client('s3') as s3:
                await s3.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"batches/{batch_id}/progress.json",
                    Body=progress.json(),
                )

            await asyncio.sleep(5)  # Update progress every 5 seconds

    def _generate_error_summary(self, items: List[BatchItem]) -> Dict[str, int]:
        """Generate summary of error types"""
        error_summary = {}
        for item in items:
            if item.error:
                error_summary[item.error] = error_summary.get(item.error, 0) + 1
        return error_summary

    async def get_batch_progress(self, batch_id: str) -> BatchProgress:
        """Get current progress of a batch job"""
        async with self.session.client('s3') as s3:
            try:
                response = await s3.get_object(
                    Bucket=self.s3_bucket,
                    Key=f"batches/{batch_id}/progress.json",
                )
                progress_data = await response['Body'].read()
                return BatchProgress.parse_raw(progress_data)
            except Exception as e:
                logger.error(f"Error fetching batch progress: {str(e)}")
                return None

    async def get_batch_result(self, batch_id: str) -> BatchResult:
        """Get final results of a completed batch job"""
        async with self.session.client('s3') as s3:
            try:
                response = await s3.get_object(
                    Bucket=self.s3_bucket,
                    Key=f"batches/{batch_id}/results.json",
                )
                result_data = await response['Body'].read()
                return BatchResult.parse_raw(result_data)
            except Exception as e:
                logger.error(f"Error fetching batch results: {str(e)}")
                return None

batch_processor = BatchProcessor()
