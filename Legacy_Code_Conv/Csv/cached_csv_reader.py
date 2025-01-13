"""
AriesOne Cached CSV Reader Module

Extends CSVReader with caching capabilities for improved performance.
"""
from typing import Optional, Union, Generator
from pathlib import Path
import pandas as pd
import hashlib
import logging
from datetime import datetime, timedelta
from functools import lru_cache
import asyncio

from csv_reader import CSVReader, ParseErrorAction, MissingFieldAction

logger = logging.getLogger(__name__)

class CachedCSVReader(CSVReader):
    """CSV reader with caching support for improved performance."""
    
    def __init__(
        self,
        cache_duration: timedelta = timedelta(hours=1),
        max_cache_size: int = 100,
        **kwargs
    ):
        """Initialize cached CSV reader.
        
        Args:
            cache_duration: How long to keep cache entries
            max_cache_size: Maximum number of cached files
            **kwargs: Arguments passed to CSVReader
        """
        super().__init__(**kwargs)
        self.cache_duration = cache_duration
        self.max_cache_size = max_cache_size
        self._cache = {}
        self._cache_times = {}
        
    def _get_file_hash(self, file_path: Union[str, Path]) -> str:
        """Generate hash of file contents for cache key.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            SHA-256 hash of file contents
        """
        file_path = Path(file_path)
        hasher = hashlib.sha256()
        
        # Hash file metadata
        stats = file_path.stat()
        meta = f"{stats.st_size}_{stats.st_mtime}"
        hasher.update(meta.encode())
        
        return hasher.hexdigest()
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cache entry is valid
        """
        if cache_key not in self._cache_times:
            return False
            
        age = datetime.now() - self._cache_times[cache_key]
        return age <= self.cache_duration
        
    def _cleanup_cache(self):
        """Remove expired and excess cache entries."""
        # Remove expired entries
        now = datetime.now()
        expired = [
            key for key, time in self._cache_times.items()
            if now - time > self.cache_duration
        ]
        for key in expired:
            del self._cache[key]
            del self._cache_times[key]
            
        # Remove oldest entries if cache is too large
        while len(self._cache) > self.max_cache_size:
            oldest_key = min(
                self._cache_times.keys(),
                key=lambda k: self._cache_times[k]
            )
            del self._cache[oldest_key]
            del self._cache_times[oldest_key]
            
    @lru_cache(maxsize=1000)
    def _get_cached_row(self, cache_key: str, row_index: int) -> Optional[pd.Series]:
        """Get single cached row by index.
        
        Args:
            cache_key: Cache key for file
            row_index: Index of row to retrieve
            
        Returns:
            Cached row or None if not found
        """
        if not self._is_cache_valid(cache_key):
            return None
            
        df = self._cache.get(cache_key)
        if df is None or row_index >= len(df):
            return None
            
        return df.iloc[row_index]
        
    def read_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Read CSV file with caching.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame containing CSV data
        """
        cache_key = self._get_file_hash(file_path)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {file_path}")
            return self._cache[cache_key]
            
        # Cache miss - read file
        logger.debug(f"Cache miss for {file_path}")
        df = super().read_file(file_path)
        
        # Update cache
        self._cleanup_cache()
        self._cache[cache_key] = df
        self._cache_times[cache_key] = datetime.now()
        
        return df
        
    def read_stream(
        self,
        file_path: Union[str, Path]
    ) -> Generator[pd.DataFrame, None, None]:
        """Stream CSV with caching support.
        
        Args:
            file_path: Path to CSV file
            
        Yields:
            DataFrame chunks of CSV data
        """
        cache_key = self._get_file_hash(file_path)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {file_path}")
            df = self._cache[cache_key]
            for i in range(0, len(df), self.chunk_size):
                yield df.iloc[i:i + self.chunk_size]
            return
            
        # Cache miss - stream and cache
        logger.debug(f"Cache miss for {file_path}")
        chunks = []
        async for chunk in super().read_stream(file_path):
            chunks.append(chunk)
            yield chunk
            
        # Update cache with complete data
        self._cleanup_cache()
        df = pd.concat(chunks)
        self._cache[cache_key] = df
        self._cache_times[cache_key] = datetime.now()
        
    async def read_file_async(
        self,
        file_path: Union[str, Path]
    ) -> pd.DataFrame:
        """Asynchronously read CSV with caching.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame containing CSV data
        """
        cache_key = self._get_file_hash(file_path)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {file_path}")
            return self._cache[cache_key]
            
        # Cache miss - read file
        logger.debug(f"Cache miss for {file_path}")
        df = await super().read_file_async(file_path)
        
        # Update cache
        self._cleanup_cache()
        self._cache[cache_key] = df
        self._cache_times[cache_key] = datetime.now()
        
        return df
