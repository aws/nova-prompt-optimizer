"""
Database setup and connection management for Nova Prompt Optimizer
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create declarative base
Base = declarative_base()

# Database engines
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

# Metadata for table creation
metadata = MetaData()


def get_database_url(async_mode: bool = False) -> str:
    """Get database URL with appropriate driver"""
    url = settings.DATABASE_URL
    
    if url.startswith("sqlite:"):
        if async_mode:
            # Use aiosqlite for async SQLite
            return url.replace("sqlite:", "sqlite+aiosqlite:")
        else:
            return url
    elif url.startswith("postgresql:"):
        if async_mode:
            # Use asyncpg for async PostgreSQL
            return url.replace("postgresql:", "postgresql+asyncpg:")
        else:
            # Use psycopg2 for sync PostgreSQL
            return url.replace("postgresql:", "postgresql+psycopg2:")
    
    return url


def create_sync_engine():
    """Create synchronous database engine"""
    global engine, SessionLocal
    
    database_url = get_database_url(async_mode=False)
    
    if database_url.startswith("sqlite"):
        # SQLite-specific configuration
        engine = create_engine(
            database_url,
            echo=settings.DATABASE_ECHO,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20
            }
        )
        # Attach SQLite event listener
        event.listens_for(engine, "connect")(set_sqlite_pragma)
    else:
        # PostgreSQL or other databases
        engine = create_engine(
            database_url,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
            pool_recycle=300
        )
    
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    return engine


def create_async_engine_instance():
    """Create asynchronous database engine"""
    global async_engine, AsyncSessionLocal
    
    database_url = get_database_url(async_mode=True)
    
    if "sqlite" in database_url:
        # SQLite-specific configuration for async
        async_engine = create_async_engine(
            database_url,
            echo=settings.DATABASE_ECHO,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20
            }
        )
    else:
        # PostgreSQL or other databases
        async_engine = create_async_engine(
            database_url,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
            pool_recycle=300
        )
    
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    return async_engine


async def init_database():
    """Initialize database and create tables"""
    logger.info("Initializing database...")
    
    # Create engines
    create_sync_engine()
    create_async_engine_instance()
    
    # Import all models to ensure they're registered
    from . import user, prompt
    # TODO: Add annotation module when it's created
    # from . import annotation
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialization complete")


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db():
    """Get synchronous database session (for compatibility)"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Database event listeners for SQLite (will be attached when engine is created)
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and reliability"""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Set WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Set cache size (negative value means KB)
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        # Set temp store to memory
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


class DatabaseManager:
    """Database manager for handling connections and transactions"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
    
    async def initialize(self):
        """Initialize database manager"""
        await init_database()
        self.engine = engine
        self.async_engine = async_engine
        self.session_factory = SessionLocal
        self.async_session_factory = AsyncSessionLocal
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        async with get_async_db() as session:
            yield session
    
    async def execute_query(self, query: str, params: Optional[dict] = None):
        """Execute raw SQL query"""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            return result.fetchall()
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# Utility functions for common database operations
async def create_tables():
    """Create all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables (use with caution!)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_table_info():
    """Get information about database tables"""
    async with get_async_db() as session:
        if "sqlite" in settings.DATABASE_URL:
            result = await session.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        else:
            result = await session.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )
        
        tables = [row[0] for row in result.fetchall()]
        return tables


# Export commonly used items
__all__ = [
    "Base",
    "engine", 
    "async_engine",
    "SessionLocal",
    "AsyncSessionLocal",
    "init_database",
    "get_db",
    "get_async_db",
    "db_manager",
    "create_tables",
    "drop_tables",
    "get_table_info"
]
