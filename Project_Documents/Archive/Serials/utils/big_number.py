"""Big number utilities module."""

from typing import List, Optional
import array

class BigNumber:
    """Class for handling large numbers stored as byte arrays."""
    
    MAX_SIZE = 17  # 0x11 bytes
    
    def __init__(self, value: Optional[str] = None):
        """Initialize big number."""
        self._bytes = array.array('B', [0] * self.MAX_SIZE)
        
        if value is not None:
            self._parse(value)
    
    @property
    def bytes(self) -> array.array:
        """Get bytes array."""
        return self._bytes
    
    @property
    def is_zero(self) -> bool:
        """Check if number is zero."""
        return all(b == 0 for b in self._bytes)
    
    def _parse(self, s: str) -> None:
        """Parse string representation."""
        if not s:
            raise ValueError("Empty string")
        
        # Remove formatting characters
        s = ''.join(c for c in s if not c.isspace() and c != '-')
        
        if len(s) != self.MAX_SIZE * 2:
            raise ValueError(
                f"String must be {self.MAX_SIZE * 2} characters long"
            )
        
        # Parse hex string
        for i in range(self.MAX_SIZE):
            high = self._char_to_byte(s[i * 2])
            low = self._char_to_byte(s[i * 2 + 1])
            
            if high is None or low is None:
                raise ValueError(f"Invalid character at position {i * 2}")
            
            self._bytes[i] = (high << 4) | low
    
    @staticmethod
    def _char_to_byte(c: str) -> Optional[int]:
        """Convert character to byte value."""
        if '0' <= c <= '9':
            return ord(c) - ord('0')
        elif 'a' <= c <= 'f':
            return ord(c) - ord('a') + 10
        elif 'A' <= c <= 'F':
            return ord(c) - ord('A') + 10
        return None
    
    @staticmethod
    def _byte_to_char(b: int) -> Optional[str]:
        """Convert byte value to character."""
        if 0 <= b <= 9:
            return chr(ord('0') + b)
        elif 10 <= b <= 35:
            return chr(ord('A') + (b - 10))
        return None
    
    def __str__(self) -> str:
        """Convert to string."""
        result = []
        for b in self._bytes:
            high = self._byte_to_char(b >> 4)
            low = self._byte_to_char(b & 0x0F)
            
            if high is None or low is None:
                raise ValueError(f"Invalid byte value: {b}")
            
            result.extend([high, low])
        
        return ''.join(result)
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, BigNumber):
            return NotImplemented
        return self._bytes == other._bytes
    
    def __hash__(self) -> int:
        """Get hash value."""
        return hash(tuple(self._bytes))
