"""
Cached CSV reader implementation.
"""
from typing import List, Dict, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
import aiofiles
from ..Models.types import CsvConfig
from .reader import CsvReader

@dataclass
class CachedCsvReader(CsvReader):
    """Cached CSV reader that stores records in memory."""
    
    records: List[List[str]] = field(default_factory=list)
    current_record_index: int = -1
    binding_list: Optional[List[Dict[str, Any]]] = None

    async def initialize(self):
        """Initialize the reader and cache all records."""
        if not self._initialized:
            async for record in self.read_records():
                self.records.append(record)
            self._initialized = True

    async def move_to(self, record_index: int) -> bool:
        """Move to specific record index."""
        if record_index < -1:
            raise ValueError("Record index cannot be negative")
            
        if not self._initialized:
            await self.initialize()
            
        if record_index >= len(self.records):
            return False
            
        self.current_record_index = record_index
        return True

    async def move_next(self) -> bool:
        """Move to next record."""
        return await self.move_to(self.current_record_index + 1)

    async def move_previous(self) -> bool:
        """Move to previous record."""
        if self.current_record_index <= 0:
            return False
        return await self.move_to(self.current_record_index - 1)

    async def move_first(self) -> bool:
        """Move to first record."""
        if not self.records:
            return False
        return await self.move_to(0)

    async def move_last(self) -> bool:
        """Move to last record."""
        if not self.records:
            return False
        return await self.move_to(len(self.records) - 1)

    def get_current_record(self) -> Optional[List[str]]:
        """Get current record."""
        if not self._initialized or self.current_record_index < 0:
            return None
        return self.records[self.current_record_index]

    async def read_records(self) -> AsyncIterator[List[str]]:
        """Read all records."""
        async for record in super().read_records():
            yield record

    def get_binding_list(self) -> List[Dict[str, Any]]:
        """Get records as list of dictionaries."""
        if self.binding_list is None:
            self.binding_list = []
            headers = self.get_headers()
            
            for record in self.records:
                row = {}
                for i, value in enumerate(record):
                    header = headers[i] if headers else f"Column{i}"
                    row[header] = value
                self.binding_list.append(row)
                
        return self.binding_list

    def copy_current_record(self, array: List[str], index: int) -> int:
        """Copy current record to array."""
        record = self.get_current_record()
        if not record:
            return 0
            
        count = min(len(array) - index, len(record))
        for i in range(count):
            array[index + i] = record[i]
        return count

    async def close(self):
        """Close the reader and clear cache."""
        await super().close()
        self.records.clear()
        self.binding_list = None
        self.current_record_index = -1
        self._initialized = False
