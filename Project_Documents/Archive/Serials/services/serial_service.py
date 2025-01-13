"""Serial number service module."""

from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.serial import SerialData
from ..utils.big_number import BigNumber

class SerialService:
    """Service for handling serial numbers."""
    
    def __init__(self, db: Session):
        """Initialize serial service."""
        self.db = db
    
    def validate_serial(self, serial_str: str) -> SerialData:
        """Validate a serial number."""
        try:
            big_num = BigNumber(serial_str)
            return SerialData(data=big_num)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid serial number: {str(e)}"
            )
    
    def check_serial_status(self, serial: SerialData) -> Dict:
        """Check serial number status."""
        return {
            'is_valid': True,
            'is_demo': serial.is_demo,
            'is_expired': serial.is_expired(),
            'max_count': serial.max_count,
            'client_number': serial.client_number,
            'expiration_date': serial.expiration_date,
        }
    
    def generate_demo_serial(self) -> SerialData:
        """Generate a demo serial number."""
        return SerialData(data=BigNumber())
    
    def generate_client_serial(
        self,
        client_number: int,
        max_count: int,
        expiration_days: Optional[int] = None
    ) -> SerialData:
        """Generate a client serial number."""
        if not 0 <= client_number <= 0xFFFF:
            raise ValueError("Client number must be between 0 and 65535")
        
        if not 0 <= max_count <= 0xFF:
            raise ValueError("Max count must be between 0 and 255")
        
        # Create byte array
        big_num = BigNumber()
        bytes_arr = big_num.bytes
        
        # Set max count
        bytes_arr[0] = max_count
        
        # Set expiration date
        if expiration_days is not None:
            if not 0 <= expiration_days <= 0x37b9da:  # Max days
                raise ValueError("Expiration days out of range")
            
            bytes_arr[4] = expiration_days & 0xFF
            bytes_arr[5] = (expiration_days >> 8) & 0xFF
            bytes_arr[6] = (expiration_days >> 16) & 0xFF
        
        # Set client number
        bytes_arr[7] = client_number & 0xFF
        bytes_arr[8] = (client_number >> 8) & 0xFF
        
        # Calculate checksum (XOR of first 16 bytes)
        checksum = 0
        for i in range(16):
            checksum ^= bytes_arr[i]
        
        # Set checksum
        bytes_arr[16] = checksum
        
        return SerialData(data=big_num)
