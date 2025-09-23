#!/usr/bin/env python3
"""
Create database tables for the Contract Risk Analyzer.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.core.database import get_database_manager
from backend.app.core.security import SecurityBase


async def create_tables():
	"""Create all database tables."""
	print("🔧 Creating database tables...")

	try:
		# Get database manager
		db_manager = await get_database_manager()

		# Create tables using SQLAlchemy metadata
		if db_manager.engine:
			async with db_manager.engine.begin() as conn:
				await conn.run_sync(SecurityBase.metadata.create_all)
				print("✅ Database tables created successfully!")
		else:
			print("❌ No database engine available")
			return False

		return True

	except Exception as e:
		print(f"❌ Table creation failed: {e}")
		import traceback

		traceback.print_exc()
		return False


if __name__ == "__main__":
	success = asyncio.run(create_tables())
	sys.exit(0 if success else 1)
