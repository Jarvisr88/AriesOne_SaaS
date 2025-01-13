"""Database sharding module."""

import hashlib
from typing import Any, Dict, List, Optional, Tuple, Type
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.sql import Select
from app.core.config import settings

class ShardKey:
    """Shard key generator."""
    
    @staticmethod
    def hash(value: Any) -> int:
        """Generate hash for sharding."""
        if not isinstance(value, str):
            value = str(value)
        
        hash_value = hashlib.md5(value.encode()).hexdigest()
        return int(hash_value, 16)
    
    @staticmethod
    def get_shard_id(hash_value: int, num_shards: int) -> int:
        """Get shard ID from hash value."""
        return hash_value % num_shards

class ShardManager:
    """Manager for database shards."""
    
    def __init__(
        self,
        shard_urls: List[str],
        Base: Type[Any]
    ):
        """Initialize shard manager."""
        self.shard_count = len(shard_urls)
        self.engines = {}
        self.sessions = {}
        self.Base = Base
        
        # Create engines for each shard
        for i, url in enumerate(shard_urls):
            self.engines[i] = create_engine(
                url,
                pool_size=settings.SHARD_POOL_SIZE,
                max_overflow=settings.SHARD_MAX_OVERFLOW
            )
    
    def setup_shards(self) -> None:
        """Create tables on all shards."""
        for engine in self.engines.values():
            self.Base.metadata.create_all(engine)
    
    def get_session(self, shard_id: int) -> Session:
        """Get session for specific shard."""
        if shard_id not in self.sessions:
            if shard_id not in self.engines:
                raise ValueError(f"Invalid shard ID: {shard_id}")
            
            self.sessions[shard_id] = Session(self.engines[shard_id])
        
        return self.sessions[shard_id]
    
    def get_shard_for_key(self, key: Any) -> int:
        """Get shard ID for key."""
        hash_value = ShardKey.hash(key)
        return ShardKey.get_shard_id(hash_value, self.shard_count)
    
    def execute_on_all_shards(
        self,
        query: Select,
        combine_results: bool = True
    ) -> List[Any]:
        """Execute query on all shards."""
        results = []
        
        for shard_id in range(self.shard_count):
            session = self.get_session(shard_id)
            shard_results = session.execute(query).fetchall()
            
            if combine_results:
                results.extend(shard_results)
            else:
                results.append((shard_id, shard_results))
        
        return results
    
    def close_all(self) -> None:
        """Close all sessions and engines."""
        for session in self.sessions.values():
            session.close()
        
        for engine in self.engines.values():
            engine.dispose()

class ShardedEntity:
    """Mixin for sharded entities."""
    
    @classmethod
    def create(
        cls,
        shard_manager: ShardManager,
        shard_key: Any,
        **kwargs: Any
    ) -> Any:
        """Create entity in appropriate shard."""
        shard_id = shard_manager.get_shard_for_key(shard_key)
        session = shard_manager.get_session(shard_id)
        
        entity = cls(**kwargs)
        session.add(entity)
        session.commit()
        
        return entity
    
    @classmethod
    def get_by_key(
        cls,
        shard_manager: ShardManager,
        shard_key: Any,
        **kwargs: Any
    ) -> Optional[Any]:
        """Get entity by key from appropriate shard."""
        shard_id = shard_manager.get_shard_for_key(shard_key)
        session = shard_manager.get_session(shard_id)
        
        return session.query(cls).filter_by(**kwargs).first()
    
    @classmethod
    def update_by_key(
        cls,
        shard_manager: ShardManager,
        shard_key: Any,
        filter_by: Dict[str, Any],
        update_values: Dict[str, Any]
    ) -> bool:
        """Update entity by key in appropriate shard."""
        shard_id = shard_manager.get_shard_for_key(shard_key)
        session = shard_manager.get_session(shard_id)
        
        result = session.query(cls).filter_by(
            **filter_by
        ).update(update_values)
        
        session.commit()
        return result > 0
    
    @classmethod
    def delete_by_key(
        cls,
        shard_manager: ShardManager,
        shard_key: Any,
        **kwargs: Any
    ) -> bool:
        """Delete entity by key from appropriate shard."""
        shard_id = shard_manager.get_shard_for_key(shard_key)
        session = shard_manager.get_session(shard_id)
        
        result = session.query(cls).filter_by(**kwargs).delete()
        session.commit()
        
        return result > 0

class ShardingMiddleware:
    """Middleware for handling sharded requests."""
    
    def __init__(self, shard_manager: ShardManager):
        """Initialize sharding middleware."""
        self.shard_manager = shard_manager
    
    def get_shard_key_from_request(
        self,
        request: Any,
        key_extractor: Optional[callable] = None
    ) -> Tuple[Any, int]:
        """Extract shard key from request."""
        if key_extractor:
            shard_key = key_extractor(request)
        else:
            # Default to user ID or client IP
            shard_key = (
                getattr(request, 'user_id', None)
                or request.client.host
            )
        
        shard_id = self.shard_manager.get_shard_for_key(shard_key)
        return shard_key, shard_id
