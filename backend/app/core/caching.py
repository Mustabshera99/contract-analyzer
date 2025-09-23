"""
Comprehensive caching system for the contract analyzer application.
Provides Redis-based caching with fallback to in-memory caching.
"""

import hashlib
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import redis
from redis.exceptions import ConnectionError, RedisError

from .config import get_settings

logger = logging.getLogger(__name__)


class CacheManager:
	"""Centralized cache management with Redis and in-memory fallback."""

	def __init__(self):
		self.settings = get_settings()
		self.redis_client = None
		self.memory_cache = {}
		self.cache_stats = {"hits": 0, "misses": 0, "errors": 0, "memory_hits": 0, "redis_hits": 0}

		# Initialize Redis connection
		self._init_redis()

	def _init_redis(self):
		"""Initialize Redis connection with proper error handling."""
		try:
			if self.settings.enable_redis_caching:
				self.redis_client = redis.Redis(
					host=self.settings.redis_host,
					port=self.settings.redis_port,
					db=self.settings.redis_db,
					password=self.settings.redis_password,
					decode_responses=False,  # We'll handle encoding ourselves
					socket_connect_timeout=5,
					socket_timeout=5,
					retry_on_timeout=True,
					health_check_interval=30,
				)
				# Test connection
				self.redis_client.ping()
				logger.info("Redis cache initialized successfully")
			else:
				logger.info("Redis caching disabled, using memory cache only")
		except (ConnectionError, RedisError) as e:
			logger.warning(f"Redis connection failed: {e}. Falling back to memory cache.")
			self.redis_client = None

	def _generate_cache_key(self, prefix: str, data: Any) -> str:
		"""Generate a consistent cache key from data."""
		# Create a hash of the data for consistent key generation
		data_str = json.dumps(data, sort_keys=True, default=str)
		data_hash = hashlib.md5(data_str.encode()).hexdigest()
		return f"{prefix}:{data_hash}"

	def _serialize_data(self, data: Any) -> bytes:
		"""Serialize data for storage."""
		try:
			return pickle.dumps(data)
		except Exception as e:
			logger.error(f"Failed to serialize data: {e}")
			raise

	def _deserialize_data(self, data: bytes) -> Any:
		"""Deserialize data from storage."""
		try:
			return pickle.loads(data)
		except Exception as e:
			logger.error(f"Failed to deserialize data: {e}")
			raise

	def get(self, key: str) -> Optional[Any]:
		"""Get data from cache (Redis first, then memory)."""
		try:
			# Try Redis first
			if self.redis_client:
				try:
					data = self.redis_client.get(key)
					if data is not None:
						self.cache_stats["redis_hits"] += 1
						self.cache_stats["hits"] += 1
						return self._deserialize_data(data)
				except (ConnectionError, RedisError) as e:
					logger.warning(f"Redis get failed: {e}")
					self.cache_stats["errors"] += 1

			# Fallback to memory cache
			if key in self.memory_cache:
				cache_entry = self.memory_cache[key]
				# Check expiration
				if cache_entry["expires_at"] > time.time():
					self.cache_stats["memory_hits"] += 1
					self.cache_stats["hits"] += 1
					return cache_entry["data"]
				else:
					# Remove expired entry
					del self.memory_cache[key]

			self.cache_stats["misses"] += 1
			return None

		except Exception as e:
			logger.error(f"Cache get error: {e}")
			self.cache_stats["errors"] += 1
			return None

	def set(self, key: str, data: Any, ttl: int = 3600) -> bool:
		"""Set data in cache (Redis first, then memory)."""
		try:
			serialized_data = self._serialize_data(data)

			# Try Redis first
			if self.redis_client:
				try:
					self.redis_client.setex(key, ttl, serialized_data)
					return True
				except (ConnectionError, RedisError) as e:
					logger.warning(f"Redis set failed: {e}")
					self.cache_stats["errors"] += 1

			# Fallback to memory cache
			self.memory_cache[key] = {"data": data, "expires_at": time.time() + ttl}

			# Clean up expired entries periodically
			if len(self.memory_cache) > 1000:
				self._cleanup_memory_cache()

			return True

		except Exception as e:
			logger.error(f"Cache set error: {e}")
			self.cache_stats["errors"] += 1
			return False

	def delete(self, key: str) -> bool:
		"""Delete data from cache."""
		try:
			# Try Redis first
			if self.redis_client:
				try:
					self.redis_client.delete(key)
				except (ConnectionError, RedisError) as e:
					logger.warning(f"Redis delete failed: {e}")

			# Remove from memory cache
			if key in self.memory_cache:
				del self.memory_cache[key]

			return True

		except Exception as e:
			logger.error(f"Cache delete error: {e}")
			return False

	def _cleanup_memory_cache(self):
		"""Clean up expired entries from memory cache."""
		current_time = time.time()
		expired_keys = [key for key, entry in self.memory_cache.items() if entry["expires_at"] <= current_time]

		for key in expired_keys:
			del self.memory_cache[key]

		logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

	def get_stats(self) -> Dict[str, Any]:
		"""Get cache statistics."""
		total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
		hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0

		return {
			"hit_rate": hit_rate,
			"total_hits": self.cache_stats["hits"],
			"total_misses": self.cache_stats["misses"],
			"redis_hits": self.cache_stats["redis_hits"],
			"memory_hits": self.cache_stats["memory_hits"],
			"errors": self.cache_stats["errors"],
			"memory_cache_size": len(self.memory_cache),
			"redis_connected": self.redis_client is not None,
		}

	def clear_all(self) -> bool:
		"""Clear all cache data."""
		try:
			# Clear Redis
			if self.redis_client:
				try:
					self.redis_client.flushdb()
				except (ConnectionError, RedisError) as e:
					logger.warning(f"Redis clear failed: {e}")

			# Clear memory cache
			self.memory_cache.clear()

			# Reset stats
			self.cache_stats = {"hits": 0, "misses": 0, "errors": 0, "memory_hits": 0, "redis_hits": 0}

			return True

		except Exception as e:
			logger.error(f"Cache clear error: {e}")
			return False


class DocumentCache:
	"""Specialized cache for document processing results."""

	def __init__(self, cache_manager: CacheManager):
		self.cache_manager = cache_manager
		self.document_ttl = 24 * 3600  # 24 hours
		self.analysis_ttl = 7 * 24 * 3600  # 7 days

	def get_document_hash(self, file_path: str, file_size: int, modified_time: float) -> str:
		"""Generate a hash for document identification."""
		data = f"{file_path}:{file_size}:{modified_time}"
		return hashlib.sha256(data.encode()).hexdigest()

	def get_document_text(self, document_hash: str) -> Optional[str]:
		"""Get cached document text."""
		key = f"document_text:{document_hash}"
		return self.cache_manager.get(key)

	def set_document_text(self, document_hash: str, text: str) -> bool:
		"""Cache document text."""
		key = f"document_text:{document_hash}"
		return self.cache_manager.set(key, text, self.document_ttl)

	def get_analysis_result(self, document_hash: str, analysis_type: str) -> Optional[Dict[str, Any]]:
		"""Get cached analysis result."""
		key = f"analysis:{analysis_type}:{document_hash}"
		return self.cache_manager.get(key)

	def set_analysis_result(self, document_hash: str, analysis_type: str, result: Dict[str, Any]) -> bool:
		"""Cache analysis result."""
		key = f"analysis:{analysis_type}:{document_hash}"
		return self.cache_manager.set(key, result, self.analysis_ttl)

	def invalidate_document(self, document_hash: str) -> bool:
		"""Invalidate all caches for a document."""
		patterns = [f"document_text:{document_hash}", f"analysis:*:{document_hash}"]

		success = True
		for pattern in patterns:
			if "*" in pattern:
				# For pattern matching, we'd need to implement key scanning
				# For now, we'll just try common analysis types
				analysis_types = ["risk_analysis", "redline_suggestions", "email_draft"]
				for analysis_type in analysis_types:
					key = f"analysis:{analysis_type}:{document_hash}"
					success &= self.cache_manager.delete(key)
			else:
				success &= self.cache_manager.delete(pattern)

		return success


class VectorCache:
	"""Specialized cache for vector store operations."""

	def __init__(self, cache_manager: CacheManager):
		self.cache_manager = cache_manager
		self.vector_ttl = 7 * 24 * 3600  # 7 days

	def get_similar_documents(self, query_hash: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
		"""Get cached similar documents."""
		key = f"vector_similar:{query_hash}:{top_k}"
		return self.cache_manager.get(key)

	def set_similar_documents(self, query_hash: str, top_k: int, documents: List[Dict[str, Any]]) -> bool:
		"""Cache similar documents."""
		key = f"vector_similar:{query_hash}:{top_k}"
		return self.cache_manager.set(key, documents, self.vector_ttl)

	def get_precedent_clauses(self, contract_hash: str) -> Optional[List[Dict[str, Any]]]:
		"""Get cached precedent clauses."""
		key = f"precedents:{contract_hash}"
		return self.cache_manager.get(key)

	def set_precedent_clauses(self, contract_hash: str, clauses: List[Dict[str, Any]]) -> bool:
		"""Cache precedent clauses."""
		key = f"precedents:{contract_hash}"
		return self.cache_manager.set(key, clauses, self.vector_ttl)


# Global cache instances
cache_manager = CacheManager()
document_cache = DocumentCache(cache_manager)
vector_cache = VectorCache(cache_manager)


def get_cache_manager() -> CacheManager:
	"""Get the global cache manager instance."""
	return cache_manager


def get_document_cache() -> DocumentCache:
	"""Get the global document cache instance."""
	return document_cache


def get_vector_cache() -> VectorCache:
	"""Get the global vector cache instance."""
	return vector_cache


# Decorator for caching function results
def cache_result(prefix: str, ttl: int = 3600, key_func: Optional[callable] = None):
	"""Decorator to cache function results."""

	def decorator(func):
		def wrapper(*args, **kwargs):
			# Generate cache key
			if key_func:
				cache_key = key_func(*args, **kwargs)
			else:
				# Use function name and arguments
				key_data = {"func": func.__name__, "args": args, "kwargs": kwargs}
				cache_key = cache_manager._generate_cache_key(prefix, key_data)

			# Try to get from cache
			result = cache_manager.get(cache_key)
			if result is not None:
				logger.debug(f"Cache hit for {func.__name__}")
				return result

			# Execute function and cache result
			result = func(*args, **kwargs)
			cache_manager.set(cache_key, result, ttl)
			logger.debug(f"Cached result for {func.__name__}")

			return result

		return wrapper

	return decorator
