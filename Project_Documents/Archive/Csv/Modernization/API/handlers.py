"""
Request handlers for CSV processing API endpoints.
"""
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException, BackgroundTasks
from ..Models.types import ImportStatus, ErrorSeverity
from ..Models.models import CsvConfig, CsvImport
from ..Services.service import CsvService

class CsvRequestHandler:
    """Handler for CSV-related requests."""
    
    def __init__(self, service: CsvService):
        self.service = service

    async def handle_upload(
        self,
        file: UploadFile,
        config: Optional[CsvConfig] = None,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Handle CSV file upload request."""
        if not file:
            raise HTTPException(
                status_code=400,
                detail="No file provided"
            )

        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only CSV files are supported"
            )

        try:
            # Create import record
            import_record = await self.service.create_import(
                filename=file.filename,
                config=config
            )

            # Add background task for processing
            background_tasks.add_task(
                self.service.process_file,
                file=file,
                import_id=import_record.id,
                config=config
            )

            return {
                "import_id": import_record.id,
                "status": ImportStatus.PENDING,
                "message": "File upload accepted for processing"
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing upload: {str(e)}"
            )

    async def handle_status_check(
        self,
        import_id: int
    ) -> Dict[str, Any]:
        """Handle import status check request."""
        try:
            import_record = await self.service.get_import(import_id)
            
            if not import_record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import record {import_id} not found"
                )

            return {
                "import_id": import_record.id,
                "status": import_record.status,
                "filename": import_record.filename,
                "row_count": import_record.row_count,
                "error_count": import_record.error_count,
                "created_at": import_record.created_at,
                "updated_at": import_record.updated_at
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking status: {str(e)}"
            )

    async def handle_error_retrieval(
        self,
        import_id: int,
        severity: Optional[ErrorSeverity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Handle import error retrieval request."""
        try:
            import_record = await self.service.get_import(import_id)
            
            if not import_record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import record {import_id} not found"
                )

            errors = await self.service.get_import_errors(
                import_id=import_id,
                severity=severity,
                limit=limit,
                offset=offset
            )

            return {
                "import_id": import_id,
                "total_errors": import_record.error_count,
                "errors": errors
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving errors: {str(e)}"
            )

    async def handle_import_cancellation(
        self,
        import_id: int
    ) -> Dict[str, Any]:
        """Handle import cancellation request."""
        try:
            import_record = await self.service.get_import(import_id)
            
            if not import_record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import record {import_id} not found"
                )

            if import_record.status not in [
                ImportStatus.PENDING,
                ImportStatus.PROCESSING
            ]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot cancel import in status: {import_record.status}"
                )

            await self.service.cancel_import(import_id)

            return {
                "import_id": import_id,
                "status": ImportStatus.CANCELLED,
                "message": "Import cancelled successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error cancelling import: {str(e)}"
            )
