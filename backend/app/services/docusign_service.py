"""
Enhanced DocuSign integration service for contract signing
"""

import base64
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class DocuSignRecipient(BaseModel):
	"""DocuSign recipient model"""

	email: str
	name: str
	role: str = "signer"  # signer, cc, carbon_copy
	routing_order: int = 1
	client_user_id: Optional[str] = None


class DocuSignDocument(BaseModel):
	"""DocuSign document model"""

	document_id: str
	name: str
	file_extension: str
	document_base64: str  # Base64 encoded document content


class DocuSignEnvelope(BaseModel):
	"""DocuSign envelope model"""

	email_subject: str
	email_blurb: str
	documents: List[DocuSignDocument]
	recipients: List[DocuSignRecipient]
	status: str = "created"  # created, sent, delivered, signed, completed, declined, voided
	custom_fields: Optional[Dict[str, Any]] = None


class DocuSignService:
	"""Enhanced DocuSign integration service"""

	def __init__(self):
		self.settings = get_settings()
		self.client_id = getattr(self.settings, "docusign_client_id", "")
		self.client_secret = getattr(self.settings, "docusign_client_secret", "")
		self.redirect_uri = getattr(self.settings, "docusign_redirect_uri", "")
		self.scopes = getattr(self.settings, "docusign_scopes", ["signature", "impersonation"])
		self.enabled = getattr(self.settings, "docusign_enabled", False)

		self.access_token = None
		self.refresh_token = None
		self.token_expires_at = None
		self.account_id = None
		self.base_uri = None

		# Use sandbox for demo
		self.auth_server_url = "https://account-d.docusign.com"
		self.base_url = "https://demo.docusign.net/restapi/v2.1"

		logger.info(f"DocuSign service initialized: enabled={self.enabled}")

	def get_authorization_url(self) -> Optional[str]:
		"""Get the DocuSign authorization URL"""
		if not self.enabled:
			return None

		params = {
			"response_type": "code",
			"scope": " ".join(self.scopes),
			"client_id": self.client_id,
			"redirect_uri": self.redirect_uri,
		}
		return f"{self.auth_server_url}/oauth/auth?{urlencode(params)}"

	async def handle_oauth_callback(self, code: str) -> bool:
		"""Handle the OAuth callback from DocuSign"""
		if not self.enabled:
			return False

		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(
					f"{self.auth_server_url}/oauth/token",
					headers={"Content-Type": "application/x-www-form-urlencoded"},
					data={
						"grant_type": "authorization_code",
						"code": code,
						"client_id": self.client_id,
						"client_secret": self.client_secret,
						"redirect_uri": self.redirect_uri,
					},
				)
				response.raise_for_status()
				token_data = response.json()

				self.access_token = token_data["access_token"]
				self.refresh_token = token_data.get("refresh_token")
				self.token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])

				await self._get_user_info()
				logger.info("DocuSign OAuth callback handled successfully")
				return True
		except Exception as e:
			logger.error(f"DocuSign OAuth callback failed: {e}")
			return False

	async def _get_user_info(self):
		"""Get user information from DocuSign"""
		if not self.access_token:
			return

		try:
			async with httpx.AsyncClient() as client:
				response = await client.get(
					f"{self.auth_server_url}/oauth/userinfo",
					headers={"Authorization": f"Bearer {self.access_token}"},
				)
				response.raise_for_status()
				user_info = response.json()
				accounts = user_info.get("accounts", [])
				if accounts:
					self.account_id = accounts[0].get("account_id")
					self.base_uri = accounts[0].get("base_uri")
					self.base_url = f"{self.base_uri}/restapi/v2.1"
		except Exception as e:
			logger.error(f"Failed to get DocuSign user info: {e}")

	async def refresh_access_token(self) -> bool:
		"""Refresh the DocuSign access token"""
		if not self.refresh_token:
			return False

		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(
					f"{self.auth_server_url}/oauth/token",
					headers={"Content-Type": "application/x-www-form-urlencoded"},
					data={
						"grant_type": "refresh_token",
						"refresh_token": self.refresh_token,
						"client_id": self.client_id,
						"client_secret": self.client_secret,
					},
				)
				response.raise_for_status()
				token_data = response.json()

				self.access_token = token_data["access_token"]
				self.refresh_token = token_data.get("refresh_token", self.refresh_token)
				self.token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
				logger.info("DocuSign access token refreshed successfully")
				return True
		except Exception as e:
			logger.error(f"Failed to refresh DocuSign access token: {e}")
			return False

	async def _ensure_authenticated(self) -> bool:
		"""Ensure we have a valid access token"""
		if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
			if self.refresh_token:
				return await self.refresh_access_token()
			else:
				# Here you would typically redirect the user to the authorization URL
				# For a backend service, you might need to re-authenticate using a different grant type
				logger.warning("DocuSign access token has expired and no refresh token is available.")
				return False
		return True

	async def create_envelope(self, envelope: DocuSignEnvelope) -> Optional[str]:
		"""Create a DocuSign envelope"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return None

		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(
					f"{self.base_url}/accounts/{self.account_id}/envelopes",
					headers={
						"Authorization": f"Bearer {self.access_token}",
						"Content-Type": "application/json",
					},
					json=envelope.dict(),
				)
				response.raise_for_status()
				envelope_data = response.json()
				logger.info(f"DocuSign: Created envelope {envelope_data['envelopeId']}")
				return envelope_data["envelopeId"]
		except Exception as e:
			logger.error(f"Failed to create DocuSign envelope: {e}")
			return None

	async def send_envelope(self, envelope_id: str) -> bool:
		"""Send a DocuSign envelope for signing"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return False

		try:
			async with httpx.AsyncClient() as client:
				response = await client.put(
					f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}",
					headers={
						"Authorization": f"Bearer {self.access_token}",
						"Content-Type": "application/json",
					},
					json={"status": "sent"},
				)
				response.raise_for_status()
				logger.info(f"DocuSign: Sent envelope {envelope_id}")
				return True
		except Exception as e:
			logger.error(f"Failed to send DocuSign envelope: {e}")
			return False

	async def get_envelope_status(self, envelope_id: str) -> Optional[Dict[str, Any]]:
		"""Get envelope status"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return None

		try:
			async with httpx.AsyncClient() as client:
				response = await client.get(
					f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}",
					headers={"Authorization": f"Bearer {self.access_token}"},
				)
				response.raise_for_status()
				return response.json()
		except Exception as e:
			logger.error(f"Failed to get DocuSign envelope status: {e}")
			return None

	async def void_envelope(self, envelope_id: str, reason: str) -> bool:
		"""Void a DocuSign envelope"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return False

		try:
			async with httpx.AsyncClient() as client:
				response = await client.put(
					f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}",
					headers={
						"Authorization": f"Bearer {self.access_token}",
						"Content-Type": "application/json",
					},
					json={"status": "voided", "voidedReason": reason},
				)
				response.raise_for_status()
				logger.info(f"DocuSign: Voided envelope {envelope_id}")
				return True
		except Exception as e:
			logger.error(f"Failed to void DocuSign envelope: {e}")
			return False

	async def get_document(self, envelope_id: str, document_id: str) -> Optional[bytes]:
		"""Get document from envelope"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return None

		try:
			async with httpx.AsyncClient() as client:
				response = await client.get(
					f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}/documents/{document_id}",
					headers={"Authorization": f"Bearer {self.access_token}"},
				)
				response.raise_for_status()
				return response.content
		except Exception as e:
			logger.error(f"Failed to get DocuSign document: {e}")
			return None

	async def create_contract_envelope(
		self,
		contract_name: str,
		contract_content: bytes,
		recipients: List[Dict[str, str]],
		subject: str = "Contract for Signature",
		message: str = "Please review and sign the attached contract.",
	) -> Optional[str]:
		"""Create a contract envelope for signing"""
		try:
			# Encode contract content
			contract_base64 = base64.b64encode(contract_content).decode("utf-8")

			# Create document
			document = DocuSignDocument(document_id="1", name=contract_name, file_extension="pdf", document_base64=contract_base64)

			# Create recipients
			docu_recipients = []
			for i, recipient in enumerate(recipients, 1):
				docu_recipients.append(
					DocuSignRecipient(email=recipient.get("email", ""), name=recipient.get("name", ""), role="signer", routing_order=i)
				)

			# Create envelope
			envelope = DocuSignEnvelope(
				email_subject=subject,
				email_blurb=message,
				documents=[document],
				recipients=docu_recipients,
				custom_fields={"contract_name": contract_name, "created_by": "Contract Analyzer AI", "analysis_date": datetime.now().isoformat()},
			)

			# Create and send envelope
			envelope_id = await self.create_envelope(envelope)
			if envelope_id:
				await self.send_envelope(envelope_id)
				return envelope_id

			return None

		except Exception as e:
			logger.error(f"Failed to create contract envelope: {e}")
			return None

	async def get_signing_url(self, envelope_id: str, recipient_email: str, recipient_name: str, return_url: str) -> Optional[str]:
		"""Get signing URL for a recipient"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return None

		try:
			async with httpx.AsyncClient() as client:
				response = await client.post(
					f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}/views/recipient",
					headers={
						"Authorization": f"Bearer {self.access_token}",
						"Content-Type": "application/json",
					},
					json={
						"returnUrl": return_url,
						"authenticationMethod": "none",
						"email": recipient_email,
						"userName": recipient_name,
					},
				)
				response.raise_for_status()
				view_data = response.json()
				return view_data["url"]
		except Exception as e:
			logger.error(f"Failed to get signing URL: {e}")
			return None

	async def get_account_info(self) -> Optional[Dict[str, Any]]:
		"""Get DocuSign account information"""
		if not await self._ensure_authenticated():
			logger.error("DocuSign authentication failed")
			return None

		try:
			async with httpx.AsyncClient() as client:
				response = await client.get(
					f"{self.base_url}/accounts/{self.account_id}",
					headers={"Authorization": f"Bearer {self.access_token}"},
				)
				response.raise_for_status()
				return response.json()
		except Exception as e:
			logger.error(f"Failed to get DocuSign account info: {e}")
			return None

	async def test_connection(self) -> Dict[str, Any]:
		"""Test DocuSign connection"""
		if not self.enabled:
			return {"success": False, "message": "DocuSign is not enabled"}
			
		auth_url = self.get_authorization_url()
		return {
			"success": True,
			"message": "DocuSign is enabled. To authenticate, please navigate to the following URL",
			"authorization_url": auth_url
		}

	async def get_templates(self) -> List[Dict[str, Any]]:
		"""Get available DocuSign templates"""
		if not await self._ensure_authenticated():
			return []

		try:
			async with httpx.AsyncClient() as client:
				response = await client.get(
					f"{self.base_url}/accounts/{self.account_id}/templates",
					headers={"Authorization": f"Bearer {self.access_token}"},
				)
				response.raise_for_status()
				templates_data = response.json()
				return templates_data.get("envelopeTemplates", [])
		except Exception as e:
			logger.error(f"Failed to get DocuSign templates: {e}")
			return []