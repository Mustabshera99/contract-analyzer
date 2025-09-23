#!/usr/bin/env python3
"""
Initialize the database with required tables for the Contract Risk Analyzer.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.core.config import get_settings
from backend.app.core.database import get_database_manager


async def init_database():
	"""Initialize the database with required tables."""
	print("🔧 Initializing database...")

	try:
		# Get database manager
		db_manager = await get_database_manager()

		# Create database directory if it doesn't exist
		os.makedirs("data", exist_ok=True)

		# Initialize database
		await db_manager.initialize()

		print("✅ Database initialized successfully!")

		# Test database connection
		health = await db_manager.health_check()
		print(f"📊 Database health: {health}")

		return True

	except Exception as e:
		print(f"❌ Database initialization failed: {e}")
		import traceback

		traceback.print_exc()
		return False


if __name__ == "__main__":
	success = asyncio.run(init_database())
	sys.exit(0 if success else 1)
