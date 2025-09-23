"""
Frontend configuration management.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FrontendConfig:
	"""Frontend configuration settings."""

	# Backend API Configuration
	BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

	# UI Configuration
	PAGE_TITLE: str = "Contract Risk Analyzer"
	PAGE_ICON: str = "📄"
	LAYOUT: str = "wide"

	# File Upload Configuration
	MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
	ALLOWED_FILE_TYPES: list[str] = ["pdf", "docx"]  # Fixed: Use direct list instead of parsing from env

	# Display Configuration
	RESULTS_EXPANDER_EXPANDED: bool = True
	ERROR_DISPLAY_DURATION: int = 5  # seconds


# Global config instance
config = FrontendConfig()
