"""Session management service for AriesOne SaaS platform."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import secrets
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.session import Session
from ...domain.models.user import User
from .database import DatabaseService, get_db_service
from ..cache import CacheService, get_cache_service
from ..logging import get_logger
from ..metrics import MetricsService, get_metrics_service
from ..config import get_settings

class SessionService:
    """Service for managing user sessions."""

    def __init__(
        self,
        db: DatabaseService,
        cache: CacheService,
        metrics: MetricsService,
        settings = Depends(get_settings)
    ):
        """Initialize session service."""
        self.db = db
        self.cache = cache
        self.metrics = metrics
        self.logger = get_logger(__name__)
        self.settings = settings
        
        # Session configuration
        self.session_ttl = timedelta(hours=24)
        self.cleanup_batch_size = 1000
        self.token_length = 64
        self.cache_ttl = 300  # 5 minutes

    async def create_session(
        self,
        user_id: UUID,
        ip_address: str,
        user_agent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session for a user."""
        try:
            # Generate unique token
            token = secrets.token_urlsafe(self.token_length)
            
            # Create session
            session_data = {
                "user_id": user_id,
                "token": token,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "metadata": metadata,
                "expires_at": datetime.utcnow() + self.session_ttl,
                "is_active": True
            }
            
            async with self.db.session() as db_session:
                # Create session
                session = await self.db.create(Session, session_data, session=db_session)
                
                # Cache session
                await self._cache_session(session)
                
                # Record metrics
                self.metrics.increment("session.created")
                
                return session

        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}", exc_info=True)
            self.metrics.increment("session.creation_error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create session"
            )

    async def get_session(
        self,
        token: str,
        *,
        validate: bool = True
    ) -> Optional[Session]:
        """Get session by token."""
        try:
            # Check cache first
            cached_session = await self.cache.get(f"session:{token}")
            if cached_session:
                self.metrics.increment("session.cache.hit")
                session = Session.from_dict(cached_session)
            else:
                self.metrics.increment("session.cache.miss")
                # Get from database
                async with self.db.session() as db_session:
                    query = select(Session).where(Session.token == token)
                    result = await db_session.execute(query)
                    session = result.scalar_one_or_none()
                    
                    if session:
                        await self._cache_session(session)

            if not session:
                return None

            if validate and session.is_expired:
                await self.invalidate_session(session.id)
                return None

            return session

        except Exception as e:
            self.logger.error(f"Error getting session: {str(e)}", exc_info=True)
            self.metrics.increment("session.get_error")
            return None

    async def validate_session(
        self,
        token: str
    ) -> Optional[Session]:
        """Validate and update session activity."""
        session = await self.get_session(token, validate=True)
        if not session:
            return None

        try:
            async with self.db.session() as db_session:
                # Update last activity
                session.touch()
                await db_session.commit()
                await self._cache_session(session)
                
                self.metrics.increment("session.validated")
                return session

        except Exception as e:
            self.logger.error(f"Error validating session: {str(e)}", exc_info=True)
            self.metrics.increment("session.validation_error")
            return None

    async def invalidate_session(
        self,
        session_id: UUID
    ) -> bool:
        """Invalidate a session."""
        try:
            async with self.db.session() as db_session:
                session = await db_session.get(Session, session_id)
                if session:
                    session.invalidate()
                    await db_session.commit()
                    
                    # Remove from cache
                    await self.cache.delete(f"session:{session.token}")
                    
                    self.metrics.increment("session.invalidated")
                    return True
                return False

        except Exception as e:
            self.logger.error(f"Error invalidating session: {str(e)}", exc_info=True)
            self.metrics.increment("session.invalidation_error")
            return False

    async def get_user_sessions(
        self,
        user_id: UUID,
        include_expired: bool = False
    ) -> List[Session]:
        """Get all sessions for a user."""
        try:
            async with self.db.session() as db_session:
                query = select(Session).where(Session.user_id == user_id)
                
                if not include_expired:
                    query = query.where(
                        and_(
                            Session.is_active == True,
                            Session.expires_at > datetime.utcnow()
                        )
                    )
                
                result = await db_session.execute(query)
                return list(result.scalars().all())

        except Exception as e:
            self.logger.error(f"Error getting user sessions: {str(e)}", exc_info=True)
            self.metrics.increment("session.user_sessions_error")
            return []

    async def cleanup_expired_sessions(
        self,
        batch_size: Optional[int] = None
    ) -> int:
        """Clean up expired sessions."""
        batch = batch_size or self.cleanup_batch_size
        cleaned = 0
        
        try:
            async with self.db.session() as db_session:
                # Get expired sessions
                query = select(Session).where(
                    or_(
                        Session.expires_at <= datetime.utcnow(),
                        Session.is_active == False
                    )
                ).limit(batch)
                
                result = await db_session.execute(query)
                expired_sessions = list(result.scalars().all())
                
                # Remove sessions and their cache entries
                for session in expired_sessions:
                    await db_session.delete(session)
                    await self.cache.delete(f"session:{session.token}")
                    cleaned += 1
                
                await db_session.commit()
                
                self.metrics.gauge("session.cleaned", cleaned)
                return cleaned

        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {str(e)}", exc_info=True)
            self.metrics.increment("session.cleanup_error")
            return 0

    async def extend_session(
        self,
        token: str,
        hours: int = 24
    ) -> Optional[Session]:
        """Extend session expiration time."""
        try:
            session = await self.get_session(token, validate=True)
            if not session:
                return None

            async with self.db.session() as db_session:
                session.extend(hours)
                await db_session.commit()
                await self._cache_session(session)
                
                self.metrics.increment("session.extended")
                return session

        except Exception as e:
            self.logger.error(f"Error extending session: {str(e)}", exc_info=True)
            self.metrics.increment("session.extension_error")
            return None

    async def _cache_session(self, session: Session) -> None:
        """Cache session data."""
        await self.cache.set(
            f"session:{session.token}",
            session.to_dict(),
            self.cache_ttl
        )


# FastAPI dependency
async def get_session_service(
    db: DatabaseService = Depends(get_db_service),
    cache: CacheService = Depends(get_cache_service),
    metrics: MetricsService = Depends(get_metrics_service)
) -> SessionService:
    """Get session service instance."""
    return SessionService(db, cache, metrics)
