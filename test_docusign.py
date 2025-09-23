#!/usr/bin/env python3
"""
Test script for DocuSign integration.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_docusign_config():
	"""Test DocuSign configuration."""
	print("🔐 Testing DocuSign Configuration")
	print("=" * 40)

	try:
		from backend.app.core.config import get_settings

		settings = get_settings()

		print(f"DocuSign Sandbox Client ID: {settings.docusign_sandbox_client_id}")
		print(
			f"DocuSign Sandbox Client Secret: {'*' * len(settings.docusign_sandbox_client_secret) if settings.docusign_sandbox_client_secret else 'Not set'}"
		)
		print(f"DocuSign Sandbox Redirect URI: {settings.docusign_sandbox_redirect_uri}")
		print(f"DocuSign Sandbox Scopes: {settings.docusign_sandbox_scopes}")
		print(f"DocuSign Sandbox Base URL: {settings.docusign_sandbox_base_url}")

		if settings.docusign_sandbox_client_id == "your_docusign_sandbox_client_id":
			print("\n❌ DocuSign credentials not configured yet")
			print("Please update the .env file with your actual DocuSign credentials")
			return False
		else:
			print("\n✅ DocuSign credentials configured")
			return True

	except Exception as e:
		print(f"❌ Error testing DocuSign config: {e}")
		return False


if __name__ == "__main__":
	success = test_docusign_config()
	sys.exit(0 if success else 1)
