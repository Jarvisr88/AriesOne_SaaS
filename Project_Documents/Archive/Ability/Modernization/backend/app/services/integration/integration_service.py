from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import asyncio
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.integration import (
    IntegrationLog,
    ERPSync,
    EcommerceSync,
    SupplierSync,
    EDIDocument
)

class IntegrationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.erp_config = settings.integration.erp
        self.ecommerce_config = settings.integration.ecommerce
        self.supplier_config = settings.integration.supplier
        self.edi_config = settings.integration.edi

    async def sync_with_erp(self, sync_type: str, data: Dict) -> Dict:
        """
        Synchronize data with ERP system
        """
        try:
            # Validate data before sync
            validated_data = await self.validate_erp_data(sync_type, data)

            # Create sync record
            sync_record = await ERPSync.create(
                sync_type=sync_type,
                direction='outbound',
                status='in_progress',
                data=validated_data,
                created_at=datetime.now()
            )

            try:
                # Perform sync with ERP
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.erp_config.api_url}/{sync_type}",
                        json=validated_data,
                        headers={
                            'Authorization': f'Bearer {self.erp_config.api_key}',
                            'X-Sync-ID': str(sync_record.id)
                        }
                    ) as response:
                        if response.status != 200:
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"ERP sync failed: {await response.text()}"
                            )
                        
                        result = await response.json()

                # Update sync record
                sync_record.status = 'completed'
                sync_record.response_data = result
                sync_record.completed_at = datetime.now()
                await sync_record.save()

                # Log successful sync
                await self.log_integration(
                    'erp',
                    'sync',
                    'success',
                    f"Successfully synced {sync_type} with ERP"
                )

                return result

            except Exception as e:
                # Update sync record with error
                sync_record.status = 'failed'
                sync_record.error_message = str(e)
                await sync_record.save()

                # Log error
                await self.log_integration(
                    'erp',
                    'sync',
                    'error',
                    f"ERP sync failed: {str(e)}"
                )
                raise

        except Exception as e:
            logger.error(f"Error in ERP sync: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error in ERP sync: {str(e)}"
            )

    async def sync_ecommerce(
        self,
        channel: str,
        sync_type: str,
        data: Dict
    ) -> Dict:
        """
        Synchronize data with e-commerce platforms
        """
        try:
            # Validate data
            validated_data = await self.validate_ecommerce_data(
                channel,
                sync_type,
                data
            )

            # Create sync record
            sync_record = await EcommerceSync.create(
                channel=channel,
                sync_type=sync_type,
                status='in_progress',
                data=validated_data,
                created_at=datetime.now()
            )

            try:
                # Get channel config
                channel_config = self.ecommerce_config.channels[channel]

                # Perform sync
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{channel_config.api_url}/{sync_type}",
                        json=validated_data,
                        headers={
                            'Authorization': f'Bearer {channel_config.api_key}',
                            'X-Sync-ID': str(sync_record.id)
                        }
                    ) as response:
                        if response.status != 200:
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"E-commerce sync failed: {await response.text()}"
                            )
                        
                        result = await response.json()

                # Update sync record
                sync_record.status = 'completed'
                sync_record.response_data = result
                sync_record.completed_at = datetime.now()
                await sync_record.save()

                # Log successful sync
                await self.log_integration(
                    'ecommerce',
                    'sync',
                    'success',
                    f"Successfully synced {sync_type} with {channel}"
                )

                return result

            except Exception as e:
                # Update sync record with error
                sync_record.status = 'failed'
                sync_record.error_message = str(e)
                await sync_record.save()

                # Log error
                await self.log_integration(
                    'ecommerce',
                    'sync',
                    'error',
                    f"E-commerce sync failed: {str(e)}"
                )
                raise

        except Exception as e:
            logger.error(f"Error in e-commerce sync: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error in e-commerce sync: {str(e)}"
            )

    async def process_edi_document(
        self,
        document_type: str,
        content: str
    ) -> Dict:
        """
        Process EDI documents
        """
        try:
            # Parse EDI document
            parsed_data = self.parse_edi_document(document_type, content)

            # Create EDI record
            edi_record = await EDIDocument.create(
                document_type=document_type,
                raw_content=content,
                parsed_data=parsed_data,
                status='processing',
                created_at=datetime.now()
            )

            try:
                # Process based on document type
                if document_type == '850':  # Purchase Order
                    result = await self.process_edi_purchase_order(parsed_data)
                elif document_type == '855':  # Purchase Order Acknowledgment
                    result = await self.process_edi_po_acknowledgment(parsed_data)
                elif document_type == '856':  # Advanced Shipping Notice
                    result = await self.process_edi_asn(parsed_data)
                elif document_type == '810':  # Invoice
                    result = await self.process_edi_invoice(parsed_data)
                else:
                    raise ValueError(f"Unsupported EDI document type: {document_type}")

                # Update EDI record
                edi_record.status = 'completed'
                edi_record.processed_data = result
                edi_record.completed_at = datetime.now()
                await edi_record.save()

                # Log successful processing
                await self.log_integration(
                    'edi',
                    'process',
                    'success',
                    f"Successfully processed EDI document {document_type}"
                )

                return result

            except Exception as e:
                # Update EDI record with error
                edi_record.status = 'failed'
                edi_record.error_message = str(e)
                await edi_record.save()

                # Log error
                await self.log_integration(
                    'edi',
                    'process',
                    'error',
                    f"EDI processing failed: {str(e)}"
                )
                raise

        except Exception as e:
            logger.error(f"Error processing EDI document: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing EDI document: {str(e)}"
            )

    async def sync_with_supplier(
        self,
        supplier_id: str,
        sync_type: str,
        data: Dict
    ) -> Dict:
        """
        Synchronize data with supplier systems
        """
        try:
            # Get supplier integration settings
            supplier = await self.get_supplier_integration_settings(supplier_id)

            # Create sync record
            sync_record = await SupplierSync.create(
                supplier_id=supplier_id,
                sync_type=sync_type,
                status='in_progress',
                data=data,
                created_at=datetime.now()
            )

            try:
                # Perform sync based on integration type
                if supplier.integration_type == 'api':
                    result = await self.sync_supplier_api(supplier, sync_type, data)
                elif supplier.integration_type == 'edi':
                    result = await self.sync_supplier_edi(supplier, sync_type, data)
                else:
                    raise ValueError(f"Unsupported integration type: {supplier.integration_type}")

                # Update sync record
                sync_record.status = 'completed'
                sync_record.response_data = result
                sync_record.completed_at = datetime.now()
                await sync_record.save()

                # Log successful sync
                await self.log_integration(
                    'supplier',
                    'sync',
                    'success',
                    f"Successfully synced {sync_type} with supplier {supplier_id}"
                )

                return result

            except Exception as e:
                # Update sync record with error
                sync_record.status = 'failed'
                sync_record.error_message = str(e)
                await sync_record.save()

                # Log error
                await self.log_integration(
                    'supplier',
                    'sync',
                    'error',
                    f"Supplier sync failed: {str(e)}"
                )
                raise

        except Exception as e:
            logger.error(f"Error in supplier sync: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error in supplier sync: {str(e)}"
            )

    async def validate_erp_data(
        self,
        sync_type: str,
        data: Dict
    ) -> Dict:
        """
        Validate data for ERP synchronization
        """
        try:
            # Get validation rules for sync type
            validation_rules = self.erp_config.validation_rules.get(sync_type)
            if not validation_rules:
                raise ValueError(f"No validation rules found for {sync_type}")

            # Validate required fields
            for field in validation_rules['required_fields']:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate data types
            for field, field_type in validation_rules['field_types'].items():
                if field in data and not isinstance(data[field], field_type):
                    raise ValueError(f"Invalid type for {field}: expected {field_type}")

            # Apply data transformations
            transformed_data = {}
            for field, value in data.items():
                transform = validation_rules['transformations'].get(field)
                transformed_data[field] = transform(value) if transform else value

            return transformed_data

        except Exception as e:
            logger.error(f"Error validating ERP data: {str(e)}")
            raise ValueError(f"Data validation failed: {str(e)}")

    async def validate_ecommerce_data(
        self,
        channel: str,
        sync_type: str,
        data: Dict
    ) -> Dict:
        """
        Validate data for e-commerce synchronization
        """
        try:
            # Get channel-specific validation rules
            validation_rules = self.ecommerce_config.channels[channel].validation_rules
            
            # Validate based on sync type
            if sync_type == 'inventory':
                return self.validate_inventory_data(data, validation_rules)
            elif sync_type == 'order':
                return self.validate_order_data(data, validation_rules)
            elif sync_type == 'price':
                return self.validate_price_data(data, validation_rules)
            else:
                raise ValueError(f"Unsupported sync type: {sync_type}")

        except Exception as e:
            logger.error(f"Error validating e-commerce data: {str(e)}")
            raise ValueError(f"Data validation failed: {str(e)}")

    def parse_edi_document(self, document_type: str, content: str) -> Dict:
        """
        Parse EDI document content
        """
        try:
            # Get EDI parser for document type
            parser = self.edi_config.parsers.get(document_type)
            if not parser:
                raise ValueError(f"No parser found for EDI document type {document_type}")

            # Parse document
            parsed_data = parser.parse(content)

            # Validate parsed data
            self.validate_edi_data(document_type, parsed_data)

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing EDI document: {str(e)}")
            raise ValueError(f"EDI parsing failed: {str(e)}")

    async def log_integration(
        self,
        integration_type: str,
        action: str,
        status: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> IntegrationLog:
        """
        Log integration activity
        """
        try:
            return await IntegrationLog.create(
                integration_type=integration_type,
                action=action,
                status=status,
                message=message,
                metadata=metadata,
                created_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error logging integration: {str(e)}")
            # Don't raise exception to prevent disrupting main flow
