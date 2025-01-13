"""
Background tasks for CSV processing.
"""
from typing import Optional, Dict, Any
from fastapi import UploadFile, BackgroundTasks
from ..Models.types import ImportStatus
from ..Models.models import CsvConfig
from .processor import CsvProcessor
from .service import CsvService

class CsvBackgroundTasks:
    """Background task handler for CSV operations."""
    
    def __init__(self, service: CsvService):
        self.service = service

    async def process_file(
        self,
        file: UploadFile,
        import_id: int,
        config: Optional[CsvConfig] = None
    ):
        """Process CSV file in background."""
        try:
            # Update status to processing
            await self.service.update_import_status(
                import_id,
                ImportStatus.PROCESSING
            )

            # Initialize processor
            processor = CsvProcessor(config or CsvConfig())
            
            # Validate file size
            if not await processor.validate_file_size(file):
                await self.service.update_import_status(
                    import_id,
                    ImportStatus.FAILED,
                    error_message="File size exceeds maximum limit"
                )
                return

            # Process file stream
            row_count = 0
            error_count = 0
            async for chunk in processor.process_stream(file):
                # Process headers if first chunk
                if row_count == 0:
                    header_result = await processor.parse_headers(chunk)
                    if not header_result.is_valid:
                        await self.service.update_import_status(
                            import_id,
                            ImportStatus.FAILED,
                            error_message="Invalid headers"
                        )
                        return
                    headers = header_result.data
                    continue

                # Process data chunk
                results = await processor.process_chunk(
                    chunk,
                    headers,
                    start_row=row_count
                )

                # Handle results
                for result in results:
                    if result.is_valid:
                        await self.service.store_row(
                            import_id,
                            result.data
                        )
                        row_count += 1
                    else:
                        await self.service.store_errors(
                            import_id,
                            result.errors
                        )
                        error_count += 1

                # Update progress periodically
                if row_count % 1000 == 0:
                    await self.service.update_import_status(
                        import_id,
                        ImportStatus.PROCESSING,
                        row_count=row_count,
                        error_count=error_count
                    )

            # Update final status
            final_status = (
                ImportStatus.COMPLETED
                if error_count == 0
                else ImportStatus.COMPLETED
            )
            
            await self.service.update_import_status(
                import_id,
                final_status,
                row_count=row_count,
                error_count=error_count
            )

        except Exception as e:
            # Handle unexpected errors
            await self.service.update_import_status(
                import_id,
                ImportStatus.FAILED,
                error_message=str(e)
            )
            raise

        finally:
            # Cleanup
            await file.close()

    async def cleanup_old_imports(
        self,
        days: int = 30
    ):
        """Cleanup old import records and files."""
        try:
            await self.service.cleanup_old_imports(days)
        except Exception as e:
            # Log cleanup error
            pass

    async def generate_import_report(
        self,
        import_id: int,
        report_format: str = 'csv'
    ):
        """Generate report for import results."""
        try:
            await self.service.generate_report(
                import_id,
                report_format
            )
        except Exception as e:
            # Log report generation error
            pass

    async def retry_failed_import(
        self,
        import_id: int,
        config: Optional[CsvConfig] = None
    ):
        """Retry a failed import."""
        try:
            # Get original import
            import_record = await self.service.get_import(import_id)
            if not import_record:
                raise ValueError(f"Import {import_id} not found")

            if import_record.status != ImportStatus.FAILED:
                raise ValueError(
                    f"Cannot retry import with status {import_record.status}"
                )

            # Create new import record
            new_import = await self.service.create_import(
                filename=import_record.filename,
                config=config or import_record.config
            )

            # Start processing
            file = await self.service.get_import_file(import_id)
            await self.process_file(
                file=file,
                import_id=new_import.id,
                config=config
            )

        except Exception as e:
            # Log retry error
            raise
