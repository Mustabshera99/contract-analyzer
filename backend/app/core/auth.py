"""
Authentication and authorization module.
"""

from typing import Optional

from pydantic import BaseModel


class APIKey(BaseModel):
	"""API Key model."""

	key: str
	name: str
	permissions: list[str] = []
	is_active: bool = True


class User(BaseModel):
	"""User model."""

	id: str
	username: str
	email: str
	permissions: list[str] = []
	is_active: bool = True


def get_current_user() -> Optional[User]:
	"""Get current user from request context."""
	# Placeholder implementation
	return None


def verify_api_key(key: str) -> Optional[APIKey]:
	"""Verify API key."""
	# Placeholder implementation
	return None


def get_current_user_or_api_key() -> Optional[User]:
	"""Get current user or API key from request context."""
	# Placeholder implementation
	return None
