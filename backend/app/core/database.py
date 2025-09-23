"""
Enhanced database management with connection pooling and async operations.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional

import asyncpg
import chromadb
from chromadb.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DatabaseManager:
	"""Enhanced database manager with connection pooling and async operations."""

	def __init__(self):
		self.engine = None
		self.async_session = None
		self.chroma_client = None
		self.connection_pool = None
		self._initialized = False

	async def initialize(self):
		"""Initialize database connections and pools."""
		if self._initialized:
			return

		try:
			# Initialize database connection pool
			if hasattr(settings, "database_url") and settings.database_url:
				self.engine = create_async_engine(
					settings.database_url,
					pool_size=20,
					max_overflow=30,
					pool_pre_ping=True,
					pool_recycle=3600,
					echo=settings.api_debug,
				)
				self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

			# Initialize ChromaDB with connection pooling
			self.chroma_client = chromadb.PersistentClient(
				path=settings.chroma_persist_directory, settings=Settings(allow_reset=True, anonymized_telemetry=False, is_persistent=True)
			)

			# Initialize Redis connection pool
			if settings.enable_redis_caching:
				import redis.asyncio as redis

				self.redis_pool = redis.ConnectionPool(
					host=settings.redis_host,
					port=settings.redis_port,
					db=settings.redis_db,
					password=settings.redis_password,
					max_connections=settings.redis_max_connections,
					socket_timeout=settings.redis_socket_timeout,
					socket_connect_timeout=settings.redis_socket_connect_timeout,
					retry_on_timeout=True,
				)
				self.redis_client = redis.Redis(connection_pool=self.redis_pool)

			self._initialized = True
			logger.info("Database manager initialized successfully")

		except Exception as e:
			logger.error(f"Failed to initialize database manager: {e}")
			raise

	@asynccontextmanager
	async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
		"""Get async database session with proper cleanup."""
		if not self.async_session:
			raise RuntimeError("Database not initialized")

		async with self.async_session() as session:
			try:
				yield session
				await session.commit()
			except Exception:
				await session.rollback()
				raise
			finally:
				await session.close()

	async def get_chroma_collection(self, collection_name: str = None):
		"""Get ChromaDB collection with error handling."""
		if not self.chroma_client:
			raise RuntimeError("ChromaDB not initialized")

		collection_name = collection_name or settings.chroma_collection_name
		try:
			return self.chroma_client.get_collection(collection_name)
		except Exception:
			# Create collection if it doesn't exist
			return self.chroma_client.create_collection(collection_name)

	async def cache_get(self, key: str) -> Optional[Any]:
		"""Get value from Redis cache."""
		if not hasattr(self, "redis_client"):
			return None

		try:
			value = await self.redis_client.get(key)
			return value.decode("utf-8") if value else None
		except Exception as e:
			logger.warning(f"Cache get failed for key {key}: {e}")
			return None

	async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
		"""Set value in Redis cache with TTL."""
		if not hasattr(self, "redis_client"):
			return False

		try:
			await self.redis_client.setex(key, ttl, str(value))
			return True
		except Exception as e:
			logger.warning(f"Cache set failed for key {key}: {e}")
			return False

	async def cache_delete(self, key: str) -> bool:
		"""Delete value from Redis cache."""
		if not hasattr(self, "redis_client"):
			return False

		try:
			await self.redis_client.delete(key)
			return True
		except Exception as e:
			logger.warning(f"Cache delete failed for key {key}: {e}")
			return False

	async def health_check(self) -> Dict[str, Any]:
		"""Check database health status."""
		health_status = {"postgresql": False, "chromadb": False, "redis": False, "timestamp": datetime.utcnow().isoformat()}

		# Check PostgreSQL
		if self.async_session:
			try:
				async with self.get_session() as session:
					await session.execute("SELECT 1")
					health_status["postgresql"] = True
			except Exception as e:
				logger.error(f"PostgreSQL health check failed: {e}")

		# Check ChromaDB
		if self.chroma_client:
			try:
				collections = self.chroma_client.list_collections()
				health_status["chromadb"] = True
			except Exception as e:
				logger.error(f"ChromaDB health check failed: {e}")

		# Check Redis
		if hasattr(self, "redis_client"):
			try:
				await self.redis_client.ping()
				health_status["redis"] = True
			except Exception as e:
				logger.error(f"Redis health check failed: {e}")

		return health_status

	async def close(self):
		"""Close all database connections."""
		if self.engine:
			await self.engine.dispose()

		if hasattr(self, "redis_pool"):
			await self.redis_pool.disconnect()

		self._initialized = False
		logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


async def get_database_manager() -> DatabaseManager:
	"""Get the global database manager instance."""
	if not db_manager._initialized:
		await db_manager.initialize()
	return db_manager


@asynccontextmanager
async def get_db_session():
	"""Dependency for getting database session."""
	manager = await get_database_manager()
	async with manager.get_session() as session:
		yield session


@asynccontextmanager
async def get_chroma_collection(collection_name: str = None):
	"""Dependency for getting ChromaDB collection."""
	manager = await get_database_manager()
	collection = await manager.get_chroma_collection(collection_name)
	yield collection
