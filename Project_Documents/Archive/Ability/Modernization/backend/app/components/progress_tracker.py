from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from app.core.config import settings
from app.models.file import FileStatus, ProcessingError
from app.services.streaming import StreamingService
from app.core.logging import logger

class ProgressTracker:
    def __init__(self, streaming_service: Optional[StreamingService] = None):
        self.streaming_service = streaming_service or StreamingService()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def start_task(
        self,
        task_id: str,
        total_items: int,
        user_id: str,
        task_type: str = "file_processing"
    ) -> None:
        """Start tracking a new task"""
        async with self._lock:
            self._tasks[task_id] = {
                "start_time": datetime.now(),
                "total_items": total_items,
                "processed_items": 0,
                "failed_items": 0,
                "user_id": user_id,
                "task_type": task_type,
                "status": "PROCESSING",
                "errors": [],
                "last_update": datetime.now()
            }
            
            await self._publish_status(task_id)

    async def update_progress(
        self,
        task_id: str,
        processed_items: int,
        failed_items: int = 0,
        errors: List[ProcessingError] = None
    ) -> None:
        """Update task progress"""
        async with self._lock:
            if task_id not in self._tasks:
                logger.warning(f"Task {task_id} not found")
                return

            task = self._tasks[task_id]
            task["processed_items"] = processed_items
            task["failed_items"] = failed_items
            if errors:
                task["errors"].extend(errors)
            task["last_update"] = datetime.now()

            await self._publish_status(task_id)

    async def complete_task(
        self,
        task_id: str,
        success: bool = True,
        errors: List[ProcessingError] = None
    ) -> None:
        """Mark task as completed"""
        async with self._lock:
            if task_id not in self._tasks:
                logger.warning(f"Task {task_id} not found")
                return

            task = self._tasks[task_id]
            task["status"] = "COMPLETED" if success else "FAILED"
            if errors:
                task["errors"].extend(errors)
            task["last_update"] = datetime.now()

            await self._publish_status(task_id)

            # Clean up task after delay
            asyncio.create_task(self._cleanup_task(task_id))

    async def fail_task(
        self,
        task_id: str,
        error: str,
        errors: List[ProcessingError] = None
    ) -> None:
        """Mark task as failed"""
        async with self._lock:
            if task_id not in self._tasks:
                logger.warning(f"Task {task_id} not found")
                return

            task = self._tasks[task_id]
            task["status"] = "FAILED"
            task["errors"].append(
                ProcessingError(
                    line=0,
                    column="",
                    message=error,
                    severity="ERROR"
                )
            )
            if errors:
                task["errors"].extend(errors)
            task["last_update"] = datetime.now()

            await self._publish_status(task_id)

            # Clean up task after delay
            asyncio.create_task(self._cleanup_task(task_id))

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

            total_items = task["total_items"]
            processed_items = task["processed_items"]
            progress = (processed_items / total_items * 100) if total_items > 0 else 0

            return {
                "task_id": task_id,
                "status": task["status"],
                "progress": progress,
                "processed_items": processed_items,
                "failed_items": task["failed_items"],
                "total_items": total_items,
                "errors": task["errors"],
                "start_time": task["start_time"],
                "last_update": task["last_update"],
                "processing_time": (
                    task["last_update"] - task["start_time"]
                ).total_seconds()
            }

    async def _publish_status(self, task_id: str) -> None:
        """Publish task status update"""
        task = self._tasks[task_id]
        total_items = task["total_items"]
        processed_items = task["processed_items"]
        progress = (processed_items / total_items * 100) if total_items > 0 else 0

        await self.streaming_service.publish_status(
            task_id,
            FileStatus(
                file_id=task_id,
                status=task["status"],
                progress=progress,
                errors=task["errors"],
                updated_at=task["last_update"]
            ),
            task["user_id"]
        )

    async def _cleanup_task(self, task_id: str) -> None:
        """Clean up completed task after delay"""
        await asyncio.sleep(settings.TASK_CLEANUP_DELAY)
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]

    def get_active_tasks(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get all active tasks, optionally filtered by user"""
        tasks = []
        for task_id, task in self._tasks.items():
            if user_id and task["user_id"] != user_id:
                continue
            if task["status"] == "PROCESSING":
                tasks.append({
                    "task_id": task_id,
                    "type": task["task_type"],
                    "progress": (task["processed_items"] / task["total_items"] * 100),
                    "start_time": task["start_time"],
                    "last_update": task["last_update"]
                })
        return tasks
