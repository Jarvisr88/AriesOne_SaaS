"""Serial number models module."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator
from ..utils.big_number import BigNumber

class SerialData(BaseModel):
    """Model for serial number data."""
    
    data: BigNumber
    
    @validator('data')
    def validate_checksum(cls, v: BigNumber) -> BigNumber:
        """Validate serial number checksum."""
        # Calculate XOR checksum of first 16 bytes
        checksum = 0
        for i in range(16):
            checksum ^= v.bytes[i]
        
        # Verify checksum and last byte
        if checksum != 0 or v.bytes[16] != 0:
            raise ValueError("Invalid serial number checksum")
        
        return v
    
    @property
    def max_count(self) -> int:
        """Get maximum count."""
        return self.data.bytes[0]
    
    @property
    def expiration_date(self) -> Optional[datetime]:
        """Get expiration date."""
        b4, b5, b6 = self.data.bytes[4:7]
        
        if b4 == 0 and b5 == 0 and b6 == 0:
            return None  # No expiration
        
        # Convert bytes to days since epoch
        days = min(b4 + (0x100 * (b5 + (0x100 * b6))), 0x37b9da)
        seconds = days * 24 * 60 * 60
        
        return datetime.fromtimestamp(seconds)
    
    @property
    def client_number(self) -> int:
        """Get client number."""
        return self.data.bytes[7] + (0x100 * self.data.bytes[8])
    
    @property
    def is_demo(self) -> bool:
        """Check if this is a demo serial."""
        return self.data.is_zero
    
    def is_expired(self) -> bool:
        """Check if serial is expired."""
        if self.is_demo:
            return False
        
        exp_date = self.expiration_date
        if exp_date is None:
            return False
        
        return exp_date < datetime.now()
    
    def __str__(self) -> str:
        """Convert to string."""
        return str(self.data)
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
