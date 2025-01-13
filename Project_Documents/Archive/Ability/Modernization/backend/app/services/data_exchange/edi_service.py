from typing import Dict, List, Optional
from datetime import datetime
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.data_exchange import (
    EDIDocument,
    EDIPartner,
    EDITransaction,
    EDIMapping
)

class EDIService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.supported_formats = ["X12", "EDIFACT", "JSON"]
        self.transaction_sets = {
            "X12": {
                "850": "Purchase Order",
                "855": "Purchase Order Acknowledgment",
                "856": "Advance Ship Notice",
                "810": "Invoice",
                "820": "Payment Order",
                "997": "Functional Acknowledgment"
            },
            "EDIFACT": {
                "ORDERS": "Purchase Order",
                "ORDRSP": "Purchase Order Response",
                "DESADV": "Dispatch Advice",
                "INVOIC": "Invoice",
                "PAYORD": "Payment Order",
                "CONTRL": "Syntax and Service Report"
            }
        }

    async def process_incoming_edi(
        self,
        partner_id: str,
        format_type: str,
        content: str
    ) -> Dict:
        """Process incoming EDI document"""
        try:
            # Validate partner and format
            partner = await self._validate_partner(partner_id, format_type)
            
            # Parse document
            parsed_data = await self._parse_edi_document(
                format_type,
                content
            )
            
            # Create document record
            document = await EDIDocument.create(
                partner_id=partner_id,
                format_type=format_type,
                direction="inbound",
                raw_content=content,
                parsed_content=parsed_data,
                status="received",
                created_at=datetime.now()
            )
            
            # Process transactions
            transactions = await self._process_transactions(
                document,
                parsed_data
            )
            
            # Update document status
            document.status = "processed"
            document.processed_at = datetime.now()
            await document.save()
            
            return {
                "status": "success",
                "document_id": str(document.id),
                "transactions": transactions
            }
        except Exception as e:
            logger.error(f"Failed to process EDI document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_edi(
        self,
        partner_id: str,
        transaction_type: str,
        data: Dict
    ) -> Dict:
        """Generate EDI document"""
        try:
            # Get partner preferences
            partner = await EDIPartner.get(id=partner_id)
            if not partner:
                raise ValueError(f"Partner not found: {partner_id}")
            
            format_type = partner.preferred_format
            
            # Validate transaction type
            if not self._is_valid_transaction(format_type, transaction_type):
                raise ValueError(f"Invalid transaction type: {transaction_type}")
            
            # Get mapping
            mapping = await self._get_mapping(
                partner_id,
                format_type,
                transaction_type
            )
            
            # Transform data
            edi_content = await self._transform_to_edi(
                format_type,
                transaction_type,
                data,
                mapping
            )
            
            # Create document record
            document = await EDIDocument.create(
                partner_id=partner_id,
                format_type=format_type,
                transaction_type=transaction_type,
                direction="outbound",
                raw_content=edi_content,
                original_data=data,
                status="generated",
                created_at=datetime.now()
            )
            
            return {
                "status": "success",
                "document_id": str(document.id),
                "content": edi_content
            }
        except Exception as e:
            logger.error(f"Failed to generate EDI document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def register_partner(
        self,
        partner_data: Dict
    ) -> EDIPartner:
        """Register new EDI partner"""
        try:
            # Validate partner data
            self._validate_partner_data(partner_data)
            
            # Create partner
            partner = await EDIPartner.create(
                name=partner_data["name"],
                identifier=partner_data["identifier"],
                preferred_format=partner_data["preferred_format"],
                settings=partner_data.get("settings", {}),
                is_active=True,
                created_at=datetime.now()
            )
            
            return partner
        except Exception as e:
            logger.error(f"Failed to register EDI partner: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_mapping(
        self,
        mapping_data: Dict
    ) -> EDIMapping:
        """Create EDI mapping"""
        try:
            # Validate mapping data
            self._validate_mapping_data(mapping_data)
            
            # Create mapping
            mapping = await EDIMapping.create(
                partner_id=mapping_data["partner_id"],
                format_type=mapping_data["format_type"],
                transaction_type=mapping_data["transaction_type"],
                field_mappings=mapping_data["field_mappings"],
                transformation_rules=mapping_data.get("transformation_rules", {}),
                created_at=datetime.now()
            )
            
            return mapping
        except Exception as e:
            logger.error(f"Failed to create EDI mapping: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _validate_partner(
        self,
        partner_id: str,
        format_type: str
    ) -> EDIPartner:
        """Validate EDI partner"""
        partner = await EDIPartner.get(id=partner_id)
        if not partner:
            raise ValueError(f"Partner not found: {partner_id}")
        
        if not partner.is_active:
            raise ValueError(f"Partner is inactive: {partner_id}")
        
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return partner

    async def _parse_edi_document(
        self,
        format_type: str,
        content: str
    ) -> Dict:
        """Parse EDI document based on format"""
        try:
            if format_type == "X12":
                return self._parse_x12(content)
            elif format_type == "EDIFACT":
                return self._parse_edifact(content)
            elif format_type == "JSON":
                return json.loads(content)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"EDI parsing failed: {str(e)}")
            raise

    async def _process_transactions(
        self,
        document: EDIDocument,
        parsed_data: Dict
    ) -> List[Dict]:
        """Process EDI transactions"""
        transactions = []
        
        try:
            # Extract transactions based on format
            if document.format_type == "X12":
                raw_transactions = parsed_data.get("transactions", [])
            elif document.format_type == "EDIFACT":
                raw_transactions = parsed_data.get("messages", [])
            else:
                raw_transactions = [parsed_data]
            
            # Process each transaction
            for raw_tx in raw_transactions:
                transaction = await EDITransaction.create(
                    document_id=document.id,
                    transaction_type=raw_tx.get("type"),
                    content=raw_tx,
                    status="processed",
                    created_at=datetime.now()
                )
                transactions.append({
                    "id": str(transaction.id),
                    "type": transaction.transaction_type
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Transaction processing failed: {str(e)}")
            raise

    def _is_valid_transaction(
        self,
        format_type: str,
        transaction_type: str
    ) -> bool:
        """Validate transaction type"""
        return (
            format_type in self.transaction_sets and
            transaction_type in self.transaction_sets[format_type]
        )

    async def _get_mapping(
        self,
        partner_id: str,
        format_type: str,
        transaction_type: str
    ) -> EDIMapping:
        """Get EDI mapping"""
        mapping = await EDIMapping.get(
            partner_id=partner_id,
            format_type=format_type,
            transaction_type=transaction_type
        )
        if not mapping:
            raise ValueError(
                f"Mapping not found for {format_type}/{transaction_type}"
            )
        return mapping

    async def _transform_to_edi(
        self,
        format_type: str,
        transaction_type: str,
        data: Dict,
        mapping: EDIMapping
    ) -> str:
        """Transform data to EDI format"""
        try:
            # Apply field mappings
            mapped_data = self._apply_field_mappings(
                data,
                mapping.field_mappings
            )
            
            # Apply transformation rules
            transformed_data = self._apply_transformations(
                mapped_data,
                mapping.transformation_rules
            )
            
            # Generate EDI content
            if format_type == "X12":
                return self._generate_x12(
                    transaction_type,
                    transformed_data
                )
            elif format_type == "EDIFACT":
                return self._generate_edifact(
                    transaction_type,
                    transformed_data
                )
            elif format_type == "JSON":
                return json.dumps(transformed_data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"EDI transformation failed: {str(e)}")
            raise

    def _apply_field_mappings(
        self,
        data: Dict,
        mappings: Dict
    ) -> Dict:
        """Apply field mappings to data"""
        result = {}
        for target_field, source_field in mappings.items():
            if isinstance(source_field, str):
                result[target_field] = data.get(source_field)
            elif isinstance(source_field, dict):
                if "constant" in source_field:
                    result[target_field] = source_field["constant"]
                elif "concatenate" in source_field:
                    values = [
                        data.get(field, "")
                        for field in source_field["concatenate"]
                    ]
                    result[target_field] = "".join(str(v) for v in values)
        return result

    def _apply_transformations(
        self,
        data: Dict,
        rules: Dict
    ) -> Dict:
        """Apply transformation rules to data"""
        result = data.copy()
        for field, rule in rules.items():
            if field in result:
                if rule.get("type") == "date":
                    result[field] = self._transform_date(
                        result[field],
                        rule.get("format", "%Y%m%d")
                    )
                elif rule.get("type") == "number":
                    result[field] = self._transform_number(
                        result[field],
                        rule.get("decimals", 2)
                    )
                elif rule.get("type") == "enum":
                    result[field] = rule["values"].get(
                        result[field],
                        result[field]
                    )
        return result

    def _transform_date(
        self,
        value: str,
        format: str
    ) -> str:
        """Transform date value"""
        if not value:
            return ""
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.strftime(format)
        except Exception:
            return value

    def _transform_number(
        self,
        value: float,
        decimals: int
    ) -> str:
        """Transform number value"""
        if not value:
            return "0" * (decimals + 1)
        try:
            return f"{float(value):.{decimals}f}".replace(".", "")
        except Exception:
            return "0" * (decimals + 1)

    def _validate_partner_data(self, partner_data: Dict) -> None:
        """Validate partner registration data"""
        required_fields = ["name", "identifier", "preferred_format"]
        for field in required_fields:
            if field not in partner_data:
                raise ValueError(f"Missing required field: {field}")
        
        if partner_data["preferred_format"] not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {partner_data['preferred_format']}"
            )

    def _validate_mapping_data(self, mapping_data: Dict) -> None:
        """Validate mapping data"""
        required_fields = [
            "partner_id",
            "format_type",
            "transaction_type",
            "field_mappings"
        ]
        for field in required_fields:
            if field not in mapping_data:
                raise ValueError(f"Missing required field: {field}")
        
        if mapping_data["format_type"] not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {mapping_data['format_type']}"
            )
        
        if not isinstance(mapping_data["field_mappings"], dict):
            raise ValueError("Field mappings must be a dictionary")

    def _parse_x12(self, content: str) -> Dict:
        """Parse X12 EDI document"""
        # Implement X12 parsing logic
        pass

    def _parse_edifact(self, content: str) -> Dict:
        """Parse EDIFACT document"""
        # Implement EDIFACT parsing logic
        pass

    def _generate_x12(
        self,
        transaction_type: str,
        data: Dict
    ) -> str:
        """Generate X12 EDI document"""
        # Implement X12 generation logic
        pass

    def _generate_edifact(
        self,
        transaction_type: str,
        data: Dict
    ) -> str:
        """Generate EDIFACT document"""
        # Implement EDIFACT generation logic
        pass
