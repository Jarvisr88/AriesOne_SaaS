import asyncio
from typing import AsyncGenerator, Optional
from fastapi import WebSocket
from redis.asyncio import Redis
from app.core.config import settings
from app.models.file import FileStatus
from app.core.auth import User

class StreamingService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.pubsub = self.redis.pubsub()

    async def publish_status(
        self,
        file_id: str,
        status: FileStatus,
        user_id: str
    ) -> None:
        """Publish file status updates to Redis"""
        channel = f"file_status:{file_id}:{user_id}"
        await self.redis.publish(channel, status.json())

    async def subscribe_to_file_status(
        self,
        file_id: str,
        user: User
    ) -> AsyncGenerator[FileStatus, None]:
        """Subscribe to file status updates"""
        channel = f"file_status:{file_id}:{user.id}"
        await self.pubsub.subscribe(channel)

        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    status = FileStatus.parse_raw(message["data"])
                    yield status
                await asyncio.sleep(0.1)
        finally:
            await self.pubsub.unsubscribe(channel)

    async def handle_websocket(
        self,
        websocket: WebSocket,
        file_id: str,
        user: User
    ) -> None:
        """Handle WebSocket connections for real-time updates"""
        await websocket.accept()
        channel = f"file_status:{file_id}:{user.id}"
        await self.pubsub.subscribe(channel)

        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    status = FileStatus.parse_raw(message["data"])
                    await websocket.send_json(status.dict())
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await self.pubsub.unsubscribe(channel)
            await websocket.close()

    async def stream_file_upload(
        self,
        file_id: str,
        chunk_generator: AsyncGenerator[bytes, None],
        user: User
    ) -> None:
        """Handle streaming file uploads"""
        total_size = 0
        chunk_size = 0
        async for chunk in chunk_generator:
            chunk_size = len(chunk)
            total_size += chunk_size
            
            # Store chunk in temporary storage
            await self._store_chunk(file_id, total_size, chunk)
            
            # Update upload progress
            progress = {
                "file_id": file_id,
                "bytes_uploaded": total_size,
                "chunk_size": chunk_size,
                "status": "uploading"
            }
            await self.publish_status(file_id, progress, user.id)

        # Finalize upload
        await self._finalize_upload(file_id, total_size, user)

    async def _store_chunk(
        self,
        file_id: str,
        offset: int,
        chunk: bytes
    ) -> None:
        """Store file chunk in temporary storage"""
        key = f"upload:{file_id}:chunk:{offset}"
        await self.redis.setex(key, 3600, chunk)  # Expire after 1 hour

    async def _finalize_upload(
        self,
        file_id: str,
        total_size: int,
        user: User
    ) -> None:
        """Finalize file upload by combining chunks"""
        chunks = []
        offset = 0
        
        while True:
            key = f"upload:{file_id}:chunk:{offset}"
            chunk = await self.redis.get(key)
            if not chunk:
                break
            chunks.append(chunk)
            offset += len(chunk)
            await self.redis.delete(key)

        if offset != total_size:
            raise ValueError("Upload size mismatch")

        # Combine chunks and process file
        complete_file = b"".join(chunks)
        await self._process_complete_file(file_id, complete_file, user)

    async def _process_complete_file(
        self,
        file_id: str,
        file_data: bytes,
        user: User
    ) -> None:
        """Process the complete uploaded file"""
        # Update status to processing
        status = {
            "file_id": file_id,
            "status": "processing",
            "progress": 0
        }
        await self.publish_status(file_id, status, user.id)

        try:
            # Process file using FileProcessor service
            from app.services.file_processor import FileProcessor
            processor = FileProcessor()
            await processor.process_file_data(file_id, file_data, user)

            # Update status to completed
            status = {
                "file_id": file_id,
                "status": "completed",
                "progress": 100
            }
        except Exception as e:
            # Update status to failed
            status = {
                "file_id": file_id,
                "status": "failed",
                "error": str(e)
            }
        finally:
            await self.publish_status(file_id, status, user.id)
