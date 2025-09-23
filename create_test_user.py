#!/usr/bin/env python3
"""
Create a test user for the Contract Risk Analyzer.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.core.database import get_database_manager
from backend.app.core.security import Role, SecurityLevel, SecurityManager, UserCreate


async def create_test_user():
	"""Create a test user."""
	print("🔧 Creating test user...")

	try:
		# Get database manager and security manager
		db_manager = await get_database_manager()
		security_manager = SecurityManager(db_manager)

		# Create test user
		user_data = UserCreate(username="test", email="test@example.com", password="TestPassword123!", security_level=SecurityLevel.INTERNAL)

		user = await security_manager.create_user(user_data)

		if user:
			print(f"✅ Test user created successfully!")
			print(f"   Username: {user.username}")
			print(f"   Email: {user.email}")
			print(f"   ID: {user.id}")
			return True
		else:
			print("❌ Failed to create test user")
			return False

	except Exception as e:
		print(f"❌ User creation failed: {e}")
		import traceback

		traceback.print_exc()
		return False


if __name__ == "__main__":
	success = asyncio.run(create_test_user())
	sys.exit(0 if success else 1)
