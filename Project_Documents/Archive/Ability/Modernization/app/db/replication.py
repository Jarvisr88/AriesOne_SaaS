from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from typing import Dict, Optional, List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ReplicationManager:
    def __init__(self):
        self.primary_engine = create_engine(
            settings.PRIMARY_DATABASE_URI,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
            pool_recycle=settings.POSTGRES_POOL_RECYCLE,
            pool_pre_ping=True,
        )

        self.replica_engines = {
            name: create_engine(
                uri,
                pool_size=settings.POSTGRES_POOL_SIZE,
                max_overflow=settings.POSTGRES_MAX_OVERFLOW,
                pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
                pool_recycle=settings.POSTGRES_POOL_RECYCLE,
                pool_pre_ping=True,
            )
            for name, uri in settings.REPLICA_DATABASE_URIS.items()
        }

        self.primary_session = sessionmaker(bind=self.primary_engine)
        self.replica_sessions = {
            name: sessionmaker(bind=engine)
            for name, engine in self.replica_engines.items()
        }

        self._setup_monitoring()

    def _setup_monitoring(self):
        """Setup monitoring for replication lag and health."""
        @event.listens_for(self.primary_engine, 'checkout')
        def primary_checkout(dbapi_conn, conn_record, conn_proxy):
            logger.debug("Primary connection checkout")

        for name, engine in self.replica_engines.items():
            @event.listens_for(engine, 'checkout')
            def replica_checkout(dbapi_conn, conn_record, conn_proxy, replica_name=name):
                logger.debug(f"Replica {replica_name} connection checkout")

    def get_primary_session(self) -> Session:
        """Get a session for the primary database."""
        return self.primary_session()

    def get_replica_session(self, preferred_replica: Optional[str] = None) -> Session:
        """Get a session for a replica database."""
        if preferred_replica and preferred_replica in self.replica_sessions:
            return self.replica_sessions[preferred_replica]()
        
        # Simple round-robin selection
        replicas = list(self.replica_sessions.keys())
        if not replicas:
            logger.warning("No replicas available, using primary")
            return self.get_primary_session()
        
        # Select replica with least lag
        replica_stats = self.check_replication_lag()
        best_replica = min(
            replica_stats.items(),
            key=lambda x: x[1].get('lag', float('inf'))
        )[0]
        
        return self.replica_sessions[best_replica]()

    def check_replication_lag(self) -> Dict[str, Dict]:
        """Check replication lag for all replicas."""
        stats = {}
        primary_session = self.get_primary_session()
        
        try:
            # Get primary xlog location
            primary_location = primary_session.execute(
                "SELECT pg_current_wal_lsn()"
            ).scalar()

            for name, session_factory in self.replica_sessions.items():
                replica_session = session_factory()
                try:
                    # Get replica xlog location and lag
                    replica_location = replica_session.execute(
                        "SELECT pg_last_wal_receive_lsn()"
                    ).scalar()
                    
                    lag_bytes = replica_session.execute(
                        "SELECT pg_wal_lsn_diff($1, $2)",
                        [primary_location, replica_location]
                    ).scalar()

                    stats[name] = {
                        'lag': lag_bytes,
                        'status': 'healthy' if lag_bytes < settings.MAX_REPLICATION_LAG else 'lagging'
                    }
                except Exception as e:
                    logger.error(f"Error checking replica {name}: {str(e)}")
                    stats[name] = {'status': 'error', 'error': str(e)}
                finally:
                    replica_session.close()
        finally:
            primary_session.close()

        return stats

    def ensure_replication_health(self) -> bool:
        """Check overall replication health."""
        stats = self.check_replication_lag()
        healthy_replicas = sum(
            1 for stat in stats.values()
            if stat.get('status') == 'healthy'
        )
        
        return healthy_replicas >= settings.MIN_HEALTHY_REPLICAS

    def handle_failover(self, failed_replica: str) -> None:
        """Handle replica failover."""
        logger.warning(f"Initiating failover for replica {failed_replica}")
        
        try:
            # Remove failed replica from pool
            if failed_replica in self.replica_engines:
                self.replica_engines[failed_replica].dispose()
                del self.replica_engines[failed_replica]
                del self.replica_sessions[failed_replica]
            
            # Check if we need to promote a replica to primary
            if failed_replica == 'primary':
                self._promote_replica()
        except Exception as e:
            logger.error(f"Failover failed: {str(e)}")
            raise

    def _promote_replica(self) -> None:
        """Promote the most up-to-date replica to primary."""
        stats = self.check_replication_lag()
        if not stats:
            raise Exception("No replicas available for promotion")

        # Select replica with least lag
        best_replica = min(
            stats.items(),
            key=lambda x: x[1].get('lag', float('inf'))
        )[0]

        logger.info(f"Promoting replica {best_replica} to primary")
        
        # Update connection details
        new_primary_uri = settings.REPLICA_DATABASE_URIS[best_replica]
        self.primary_engine = create_engine(
            new_primary_uri,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
            pool_recycle=settings.POSTGRES_POOL_RECYCLE,
            pool_pre_ping=True,
        )
        self.primary_session = sessionmaker(bind=self.primary_engine)

        # Remove promoted replica from replica pool
        del self.replica_engines[best_replica]
        del self.replica_sessions[best_replica]

    def get_replication_status(self) -> Dict:
        """Get comprehensive replication status."""
        stats = self.check_replication_lag()
        
        return {
            'primary': {
                'status': 'healthy',
                'connections': self.primary_engine.pool.size(),
                'active_connections': self.primary_engine.pool.checkedin()
            },
            'replicas': {
                name: {
                    **stat,
                    'connections': engine.pool.size(),
                    'active_connections': engine.pool.checkedin()
                }
                for name, (stat, engine) in zip(
                    stats.items(),
                    self.replica_engines.items()
                )
            },
            'overall_health': self.ensure_replication_health()
        }
