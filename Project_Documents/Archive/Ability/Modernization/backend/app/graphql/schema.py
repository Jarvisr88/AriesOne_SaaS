import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum
from strawberry.file_uploads import Upload
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL

from app.core.auth import get_current_user, User
from app.core.config import settings
from app.services.file_processor import FileProcessor
from app.services.streaming import StreamingService
from app.models.file import FileStatus, ProcessingError

@strawberry.enum
class FileProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@strawberry.type
class ProcessingErrorType:
    line: int
    column: str
    message: str
    severity: str

@strawberry.type
class FileMetadata:
    id: str
    filename: str
    size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    status: FileProcessingStatus
    progress: float
    row_count: Optional[int] = None
    error_count: Optional[int] = None
    errors: List[ProcessingErrorType]

@strawberry.type
class ProcessingResult:
    success: bool
    message: str
    file: Optional[FileMetadata] = None
    errors: List[ProcessingErrorType]

@strawberry.type
class Query:
    @strawberry.field
    async def get_file(self, info: Info, file_id: str) -> Optional[FileMetadata]:
        user = await get_current_user(info.context["request"])
        file_processor = FileProcessor()
        return await file_processor.get_file(file_id, user)

    @strawberry.field
    async def list_files(
        self,
        info: Info,
        status: Optional[FileProcessingStatus] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[FileMetadata]:
        user = await get_current_user(info.context["request"])
        file_processor = FileProcessor()
        return await file_processor.list_files(user, status, limit, offset)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def upload_file(
        self,
        info: Info,
        file: Upload,
        process_immediately: bool = True
    ) -> ProcessingResult:
        user = await get_current_user(info.context["request"])
        file_processor = FileProcessor()
        
        try:
            contents = await file.read()
            result = await file_processor.process_file(
                contents,
                file.filename,
                user,
                process_immediately
            )
            return ProcessingResult(
                success=True,
                message="File uploaded successfully",
                file=result
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=str(e),
                errors=[
                    ProcessingErrorType(
                        line=0,
                        column="",
                        message=str(e),
                        severity="ERROR"
                    )
                ]
            )

    @strawberry.mutation
    async def cancel_processing(
        self,
        info: Info,
        file_id: str
    ) -> ProcessingResult:
        user = await get_current_user(info.context["request"])
        file_processor = FileProcessor()
        
        try:
            result = await file_processor.cancel_processing(file_id, user)
            return ProcessingResult(
                success=True,
                message="Processing cancelled successfully",
                file=result
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=str(e),
                errors=[
                    ProcessingErrorType(
                        line=0,
                        column="",
                        message=str(e),
                        severity="ERROR"
                    )
                ]
            )

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def file_status(self, info: Info, file_id: str) -> FileMetadata:
        user = await get_current_user(info.context["request"])
        streaming_service = StreamingService()
        
        async for status in streaming_service.subscribe_to_file_status(file_id, user):
            yield status

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

graphql_app = GraphQLRouter(
    schema,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL]
)
