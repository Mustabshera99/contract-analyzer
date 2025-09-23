"""
API client for communicating with the backend service.
"""

import json
import time
from io import BytesIO
from typing import Any, Dict, Optional, Union

import requests
import streamlit as st


class APIClient:
	"""Client for backend API communication."""

	def __init__(self, base_url: str):
		self.base_url = base_url.rstrip("/")
		self.session = requests.Session()
		self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

	def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
		"""Make HTTP request with error handling."""
		url = f"{self.base_url}{endpoint}"

		try:
			response = self.session.request(method, url, **kwargs)
			response.raise_for_status()

			# Try to parse JSON response
			try:
				return response.json()
			except json.JSONDecodeError:
				return {"data": response.text}

		except requests.exceptions.ConnectionError:
			return {"error": "Unable to connect to the analysis service. Please check your connection."}
		except requests.exceptions.Timeout:
			return {"error": "Request timed out. Please try again."}
		except requests.exceptions.HTTPError as e:
			if response.status_code == 404:
				return {"error": "Service endpoint not found."}
			elif response.status_code == 500:
				return {"error": "Internal server error. Please try again later."}
			else:
				return {"error": f"HTTP error {response.status_code}: {e!s}"}
		except Exception as e:
			return {"error": f"Unexpected error: {e!s}"}

	def health_check(self) -> Dict[str, Any]:
		"""Check if the backend service is healthy."""
		return self._make_request("GET", "/api/v1/health")

	def analyze_contract_sync(self, file_obj, timeout_seconds: int = 300) -> Dict[str, Any]:
		"""
		Analyze contract synchronously.

		Args:
		    file_obj: File object to analyze
		    timeout_seconds: Request timeout

		Returns:
		    Analysis results or error
		"""
		# Prepare file for upload
		files = {"file": (file_obj.name, file_obj.getvalue(), file_obj.type)}

		# Remove Content-Type header for multipart upload
		headers = {k: v for k, v in self.session.headers.items() if k.lower() != "content-type"}

		try:
			response = self.session.post(f"{self.base_url}/api/v1/analyze-contract", files=files, headers=headers, timeout=timeout_seconds)
			response.raise_for_status()
			return response.json()

		except requests.exceptions.ConnectionError:
			return {"error": "Unable to connect to the analysis service."}
		except requests.exceptions.Timeout:
			return {"error": "Analysis timed out. Please try again with a longer timeout."}
		except requests.exceptions.HTTPError as e:
			try:
				error_data = response.json()
				return {"error": error_data.get("message", f"HTTP error {response.status_code}")}
			except:
				return {"error": f"HTTP error {response.status_code}: {e!s}"}
		except Exception as e:
			return {"error": f"Unexpected error: {e!s}"}

	def analyze_contract_async(
		self, file_obj, timeout_seconds: int = 300, priority: str = "normal", enable_progress_tracking: bool = True
	) -> Dict[str, Any]:
		"""
		Start asynchronous contract analysis.

		Args:
		    file_obj: File object to analyze
		    timeout_seconds: Analysis timeout
		    priority: Analysis priority (low, normal, high)
		    enable_progress_tracking: Enable progress updates

		Returns:
		    Task information or error
		"""
		# For now, use the synchronous endpoint as a fallback
		# TODO: Fix the async endpoint issue
		try:
			# Prepare file for upload
			# Handle Streamlit file upload object more robustly
			try:
				file_name = file_obj.name if hasattr(file_obj, "name") and file_obj.name else "uploaded_file.pdf"
			except:
				file_name = "uploaded_file.pdf"

			try:
				file_content = file_obj.getvalue() if hasattr(file_obj, "getvalue") else file_obj.read()
			except:
				file_content = b""

			try:
				file_type = file_obj.type if hasattr(file_obj, "type") and file_obj.type else "application/pdf"
			except:
				file_type = "application/pdf"

			# Ensure we have valid content
			if not file_content:
				return {"error": "No file content received"}

			files = {"file": (file_name, file_content, file_type)}

			# Use the synchronous endpoint for now
			# Create a new session without the problematic headers
			import requests

			temp_session = requests.Session()
			temp_session.headers.update({"Accept": "application/json", "X-API-Key": "demo_token", "Authorization": "Bearer demo_token"})

			response = temp_session.post(
				f"{self.base_url}/api/v1/analyze-contract",
				files=files,
				timeout=300,  # Longer timeout for analysis
			)

			response.raise_for_status()

			# Convert sync response to async format
			result = response.json()
			return {"task_id": f"sync_{int(time.time())}", "status": "completed", "result": result}

		except requests.exceptions.ConnectionError:
			return {"error": "Unable to connect to the analysis service."}
		except requests.exceptions.Timeout:
			return {"error": "Request timed out while starting analysis."}
		except requests.exceptions.HTTPError as e:
			try:
				error_data = response.json()
				return {"error": error_data.get("message", f"HTTP error {response.status_code}")}
			except:
				return {"error": f"HTTP error {response.status_code}: {e!s}"}
		except Exception as e:
			return {"error": f"Unexpected error: {e!s}"}

	def get_analysis_status(self, task_id: str) -> Dict[str, Any]:
		"""
		Get status of asynchronous analysis.

		Args:
		    task_id: Task identifier

		Returns:
		    Status information or error
		"""
		# Handle sync fallback
		if task_id.startswith("sync_"):
			return {"status": "completed", "progress": 100}

		return self._make_request("GET", f"/api/v1/analyze-contract/async/{task_id}/status")

	def get_analysis_results(self, task_id: str) -> Dict[str, Any]:
		"""
		Get results of completed analysis.

		Args:
		    task_id: Task identifier

		Returns:
		    Analysis results or error
		"""
		# Handle sync fallback - return the result that was already stored
		if task_id.startswith("sync_"):
			# For sync tasks, the result is already in the response
			return {"error": "Sync task results are returned immediately"}

		return self._make_request("GET", f"/api/v1/analyze-contract/async/{task_id}/result")

	def login(self, username, password) -> Dict[str, Any]:
		"""Authenticate user and get token."""
		return self._make_request("POST", "/api/v1/auth/login", json={"username": username, "password": password})

	def set_token(self, token: str):
		"""Set the auth token for subsequent requests."""
		self.session.headers.update({"Authorization": f"Bearer {token}"})

	def clear_token(self):
		"""Clear the auth token."""
		if "Authorization" in self.session.headers:
			del self.session.headers["Authorization"]

	def cancel_analysis(self, task_id: str) -> Dict[str, Any]:
		"""
		Cancel running analysis.

		Args:
		    task_id: Task identifier

		Returns:
		    Cancellation status or error
		"""
		return self._make_request("DELETE", f"/api/v1/analyze-contract/async/{task_id}")
