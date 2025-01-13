import asyncio
import csv
import io
from typing import AsyncGenerator, Dict, List, Optional, Any
from pydantic import BaseModel, ValidationError
from datetime import datetime
from app.core.config import settings
from app.models.file import ProcessingError, FileStatus
from app.services.streaming import StreamingService
from app.core.logging import logger

class RowData(BaseModel):
    row_number: int
    data: Dict[str, Any]
    errors: List[ProcessingError]
    is_valid: bool

class CSVProcessor:
    def __init__(self, streaming_service: Optional[StreamingService] = None):
        self.streaming_service = streaming_service or StreamingService()
        self.chunk_size = settings.CSV_CHUNK_SIZE
        self.max_errors = settings.MAX_VALIDATION_ERRORS

    async def process_stream(
        self,
        file_id: str,
        file_stream: AsyncGenerator[bytes, None],
        schema: BaseModel,
        delimiter: str = ",",
        user_id: str = None
    ) -> AsyncGenerator[RowData, None]:
        """Process CSV file as a stream with validation"""
        buffer = ""
        row_number = 0
        header = None
        total_errors = 0

        async for chunk in file_stream:
            buffer += chunk.decode("utf-8")
            lines = buffer.split("\n")
            
            # Keep the last partial line in buffer
            buffer = lines[-1]
            lines = lines[:-1]

            if not header and lines:
                header = lines[0].strip().split(delimiter)
                lines = lines[1:]

            if header:
                for line in lines:
                    row_number += 1
                    if not line.strip():
                        continue

                    try:
                        row = dict(zip(header, line.strip().split(delimiter)))
                        # Validate row against schema
                        validated_data = schema(**row)
                        yield RowData(
                            row_number=row_number,
                            data=validated_data.dict(),
                            errors=[],
                            is_valid=True
                        )
                    except ValidationError as e:
                        total_errors += 1
                        errors = [
                            ProcessingError(
                                line=row_number,
                                column=err["loc"][0],
                                message=err["msg"],
                                severity="ERROR"
                            )
                            for err in e.errors()
                        ]
                        yield RowData(
                            row_number=row_number,
                            data=row,
                            errors=errors,
                            is_valid=False
                        )

                        if total_errors >= self.max_errors:
                            raise ValueError(f"Maximum error count ({self.max_errors}) exceeded")

                    # Update progress
                    if user_id and row_number % 100 == 0:
                        await self._update_progress(file_id, row_number, user_id)

    async def process_file(
        self,
        file_id: str,
        file_path: str,
        schema: BaseModel,
        delimiter: str = ",",
        user_id: str = None
    ) -> Dict[str, Any]:
        """Process entire CSV file with validation and error tracking"""
        start_time = datetime.now()
        total_rows = 0
        valid_rows = 0
        errors = []

        try:
            # Update status to processing
            await self._update_status(
                file_id,
                "PROCESSING",
                0,
                user_id
            )

            async with aiofiles.open(file_path, mode="rb") as file:
                async for row in self.process_stream(
                    file_id,
                    self._chunk_generator(file),
                    schema,
                    delimiter,
                    user_id
                ):
                    total_rows += 1
                    if row.is_valid:
                        valid_rows += 1
                        await self._process_valid_row(row.data)
                    else:
                        errors.extend(row.errors)

            # Update final status
            success = len(errors) == 0
            status = "COMPLETED" if success else "FAILED"
            await self._update_status(
                file_id,
                status,
                100,
                user_id,
                errors=errors
            )

            return {
                "file_id": file_id,
                "total_rows": total_rows,
                "valid_rows": valid_rows,
                "error_count": len(errors),
                "errors": errors,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "success": success
            }

        except Exception as e:
            logger.error(f"Error processing file {file_id}: {str(e)}")
            await self._update_status(
                file_id,
                "FAILED",
                0,
                user_id,
                errors=[ProcessingError(
                    line=0,
                    column="",
                    message=str(e),
                    severity="ERROR"
                )]
            )
            raise

    async def _chunk_generator(
        self,
        file
    ) -> AsyncGenerator[bytes, None]:
        """Generate file chunks for streaming"""
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    async def _update_progress(
        self,
        file_id: str,
        row_number: int,
        user_id: str
    ) -> None:
        """Update processing progress"""
        await self.streaming_service.publish_status(
            file_id,
            FileStatus(
                file_id=file_id,
                status="PROCESSING",
                progress=row_number,
                updated_at=datetime.now()
            ),
            user_id
        )

    async def _update_status(
        self,
        file_id: str,
        status: str,
        progress: int,
        user_id: str,
        errors: List[ProcessingError] = None
    ) -> None:
        """Update file processing status"""
        await self.streaming_service.publish_status(
            file_id,
            FileStatus(
                file_id=file_id,
                status=status,
                progress=progress,
                errors=errors or [],
                updated_at=datetime.now()
            ),
            user_id
        )

    async def _process_valid_row(self, data: Dict[str, Any]) -> None:
        """Process a valid row of data"""
        # Implement your row processing logic here
        await asyncio.sleep(0)  # Yield control to event loop
