"""Batch processing service module."""

import os
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from redis import Redis
from ..models.document import Document, DocumentProcessingJob
from .document_scanner import DocumentScanner
from .ocr_service import OCRService

class BatchProcessor:
    """Service for handling batch document processing."""

    def __init__(self, db: Session, redis: Redis, settings: Dict):
        """Initialize the batch processor."""
        self.db = db
        self.redis = redis
        self.settings = settings
        self.scanner = DocumentScanner(db, settings)
        self.ocr_service = OCRService(db, settings)
        self.max_concurrent_jobs = settings.get('max_concurrent_jobs', 5)
        self.job_timeout = settings.get('job_timeout', 3600)  # 1 hour

    async def process_batch(self, batch_id: str, documents: List[Dict]) -> bool:
        """Process a batch of documents."""
        try:
            # Create jobs for each document
            jobs = []
            for doc in documents:
                job = self._create_job(batch_id, doc)
                jobs.append(job)
            
            # Process jobs concurrently
            await self._process_jobs(jobs)
            return True
        except Exception as e:
            print(f"Batch processing failed: {e}")
            return False

    def _create_job(self, batch_id: str, document: Dict) -> DocumentProcessingJob:
        """Create a processing job for a document."""
        job = DocumentProcessingJob(
            job_type='batch_process',
            status='pending',
            parameters={
                'batch_id': batch_id,
                'document': document,
                'options': {
                    'scan': document.get('scan_options', {}),
                    'ocr': document.get('ocr_options', {})
                }
            }
        )
        self.db.add(job)
        self.db.commit()
        return job

    async def _process_jobs(self, jobs: List[DocumentProcessingJob]) -> None:
        """Process multiple jobs concurrently."""
        # Create task semaphore
        sem = asyncio.Semaphore(self.max_concurrent_jobs)
        
        # Create tasks
        tasks = []
        for job in jobs:
            task = asyncio.create_task(self._process_job_with_semaphore(sem, job))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    async def _process_job_with_semaphore(self, sem: asyncio.Semaphore, 
                                        job: DocumentProcessingJob) -> None:
        """Process a job with semaphore control."""
        async with sem:
            await self._process_single_job(job)

    async def _process_single_job(self, job: DocumentProcessingJob) -> None:
        """Process a single document job."""
        try:
            # Update job status
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            self.db.commit()

            # Get job parameters
            params = job.parameters
            doc_params = params['document']
            options = params['options']

            # Scan document
            job.progress = 0.2
            self.db.commit()
            document = self.scanner.scan_document(
                doc_params.get('device_id'),
                options['scan']
            )
            job.document_id = document.id

            # Process with OCR
            job.progress = 0.6
            self.db.commit()
            self.ocr_service.process_document(document)

            # Update job status
            job.status = 'completed'
            job.progress = 1.0
            job.completed_at = datetime.utcnow()
            job.result = {
                'document_id': document.id,
                'page_count': document.page_count,
                'processing_time': (job.completed_at - job.started_at).total_seconds()
            }
            self.db.commit()

        except Exception as e:
            # Handle job failure
            job.status = 'failed'
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Job processing failed: {e}")

    def get_batch_status(self, batch_id: str) -> Dict:
        """Get the status of a batch processing job."""
        jobs = self.db.query(DocumentProcessingJob).filter(
            DocumentProcessingJob.parameters['batch_id'].astext == batch_id
        ).all()

        total_jobs = len(jobs)
        completed_jobs = sum(1 for job in jobs if job.status == 'completed')
        failed_jobs = sum(1 for job in jobs if job.status == 'failed')
        in_progress = sum(1 for job in jobs if job.status == 'processing')
        
        total_progress = sum(job.progress or 0 for job in jobs) / total_jobs if total_jobs else 0

        return {
            'batch_id': batch_id,
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'in_progress': in_progress,
            'overall_progress': total_progress,
            'status': 'completed' if completed_jobs == total_jobs else 'failed' if failed_jobs == total_jobs else 'processing'
        }

    def cleanup_stale_jobs(self) -> int:
        """Clean up stale processing jobs."""
        cutoff_time = datetime.utcnow().timestamp() - self.job_timeout
        stale_jobs = self.db.query(DocumentProcessingJob).filter(
            DocumentProcessingJob.status == 'processing',
            DocumentProcessingJob.started_at < cutoff_time
        ).all()

        cleaned_count = 0
        for job in stale_jobs:
            job.status = 'failed'
            job.error = 'Job timed out'
            job.completed_at = datetime.utcnow()
            cleaned_count += 1

        self.db.commit()
        return cleaned_count
