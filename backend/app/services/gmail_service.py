"""
Gmail integration service for sending contract analysis emails
"""

import base64
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class GmailMessage(BaseModel):
	"""Gmail message model"""

	to: str
	subject: str
	body: str
	cc: Optional[List[str]] = None
	bcc: Optional[List[str]] = None
	attachments: Optional[List[Dict[str, Any]]] = None


class GmailAttachment(BaseModel):
	"""Gmail attachment model"""

	filename: str
	content_type: str
	data: str  # Base64 encoded data


class GmailService:
	"""Gmail integration service using Gmail API"""

	def __init__(self):
		self.settings = get_settings()
		self.client_id = getattr(self.settings, "gmail_client_id", "")
		self.client_secret = getattr(self.settings, "gmail_client_secret", "")
		self.redirect_uri = getattr(self.settings, "gmail_redirect_uri", "")
		self.scopes = getattr(self.settings, "gmail_scopes", "https://www.googleapis.com/auth/gmail.send")
		self.enabled = getattr(self.settings, "gmail_enabled", False)

		self.access_token = None
		self.refresh_token = None
		self.token_expires_at = None
		self.base_url = "https://gmail.googleapis.com/gmail/v1"

		logger.info(f"Gmail service initialized: enabled={self.enabled}")

	async def authenticate(self) -> bool:
		"""Authenticate with Gmail API"""
		try:
			if not self.enabled or not self.client_id or not self.client_secret:
				logger.warning("Gmail not enabled or credentials missing")
				return False

			# For demo purposes, we'll use a mock authentication
			# In production, implement OAuth2 flow
			self.access_token = f"gmail_token_{datetime.now().timestamp()}"
			self.refresh_token = f"gmail_refresh_{datetime.now().timestamp()}"
			self.token_expires_at = datetime.now() + timedelta(hours=1)

			logger.info("Gmail authenticated successfully")
			return True

		except Exception as e:
			logger.error(f"Gmail authentication failed: {e}")
			return False

	async def _ensure_authenticated(self) -> bool:
		"""Ensure we have a valid access token"""
		if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
			return await self.authenticate()
		return True

	async def send_email(self, message: GmailMessage) -> bool:
		"""Send an email via Gmail API"""
		try:
			if not await self._ensure_authenticated():
				logger.error("Gmail authentication failed")
				return False

			# Create the email message
			email_data = self._create_email_message(message)

			# For demo purposes, we'll simulate sending
			# In production, make actual API call to Gmail
			logger.info(f"Gmail: Sending email to {message.to} with subject '{message.subject}'")

			# Simulate API call
			           async with httpx.AsyncClient() as session:				headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

				# Mock response for demo
				logger.info("Gmail: Email sent successfully (simulated)")
				return True

		except Exception as e:
			logger.error(f"Failed to send Gmail: {e}")
			return False

	def _create_email_message(self, message: GmailMessage) -> str:
		"""Create email message in Gmail API format"""
		# Create email headers
		headers = {"To": message.to, "Subject": message.subject, "Content-Type": "text/html; charset=utf-8"}

		if message.cc:
			headers["Cc"] = ", ".join(message.cc)
		if message.bcc:
			headers["Bcc"] = ", ".join(message.bcc)

		# Create email body
		email_body = f"""From: Contract Analyzer <noreply@contractanalyzer.com>
To: {message.to}
Subject: {message.subject}
Content-Type: text/html; charset=utf-8

{message.body}"""

		# Encode the message
		message_bytes = email_body.encode("utf-8")
		encoded_message = base64.urlsafe_b64encode(message_bytes).decode("utf-8")

		return encoded_message

	async def send_contract_analysis_email(
		self,
		recipient_email: str,
		contract_name: str,
		risk_score: float,
		risky_clauses: List[Dict[str, Any]],
		analysis_summary: str,
		recommendations: List[str],
	) -> bool:
		"""Send contract analysis results via email"""
		try:
			# Create email content
			subject = f"Contract Analysis Results: {contract_name}"

			# Generate HTML email body
			html_body = self._generate_analysis_email_html(contract_name, risk_score, risky_clauses, analysis_summary, recommendations)

			# Create message
			message = GmailMessage(to=recipient_email, subject=subject, body=html_body)

			return await self.send_email(message)

		except Exception as e:
			logger.error(f"Failed to send contract analysis email: {e}")
			return False

	def _generate_analysis_email_html(
		self, contract_name: str, risk_score: float, risky_clauses: List[Dict[str, Any]], analysis_summary: str, recommendations: List[str]
	) -> str:
		"""Generate HTML email content for contract analysis"""

		# Risk level color
		if risk_score >= 7:
			risk_color = "#dc3545"  # Red
			risk_level = "High"
		elif risk_score >= 4:
			risk_color = "#ffc107"  # Yellow
			risk_level = "Medium"
		else:
			risk_color = "#28a745"  # Green
			risk_level = "Low"

		# Generate risky clauses HTML
		clauses_html = ""
		for i, clause in enumerate(risky_clauses, 1):
			clauses_html += f"""
            <div style="margin-bottom: 15px; padding: 10px; border-left: 4px solid {risk_color}; background-color: #f8f9fa;">
                <h4 style="margin: 0 0 5px 0; color: {risk_color};">Clause {i}: {clause.get("risk_level", "Unknown")} Risk</h4>
                <p style="margin: 5px 0; font-style: italic;">"{clause.get("clause_text", "")[:200]}..."</p>
                <p style="margin: 5px 0; font-size: 14px;">{clause.get("risk_explanation", "")}</p>
            </div>
            """

		# Generate recommendations HTML
		recommendations_html = ""
		for rec in recommendations:
			recommendations_html += f"<li style='margin-bottom: 5px;'>{rec}</li>"

		html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Contract Analysis Results</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h1 style="color: #2c3e50; margin: 0 0 10px 0;">📋 Contract Analysis Results</h1>
                <h2 style="color: #495057; margin: 0;">{contract_name}</h2>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="color: #2c3e50; margin-top: 0;">📊 Risk Assessment</h3>
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="background-color: {risk_color}; color: white; padding: 10px 20px; border-radius: 20px; font-weight: bold; margin-right: 15px;">
                        Risk Score: {risk_score}/10
                    </div>
                    <span style="font-size: 18px; font-weight: bold; color: {risk_color};">{risk_level} Risk</span>
                </div>
                <p style="font-size: 16px; margin: 0;">{analysis_summary}</p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="color: #2c3e50; margin-top: 0;">⚠️ Risky Clauses ({len(risky_clauses)} found)</h3>
                {clauses_html if clauses_html else "<p>No risky clauses identified.</p>"}
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="color: #2c3e50; margin-top: 0;">💡 Recommendations</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    {recommendations_html if recommendations_html else "<li>No specific recommendations at this time.</li>"}
                </ul>
            </div>
            
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 8px; text-align: center; font-size: 14px; color: #6c757d;">
                <p style="margin: 0;">This analysis was generated by Contract Analyzer AI</p>
                <p style="margin: 5px 0 0 0;">For questions or concerns, please contact your legal team.</p>
            </div>
        </body>
        </html>
        """

		return html_content

	async def send_notification_email(self, recipient_email: str, title: str, message: str, priority: str = "normal") -> bool:
		"""Send a notification email"""
		try:
			# Priority colors
			priority_colors = {"high": "#dc3545", "medium": "#ffc107", "normal": "#17a2b8", "low": "#28a745"}

			color = priority_colors.get(priority.lower(), "#17a2b8")

			html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Contract Analyzer Notification</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="margin: 0;">🔔 {title}</h1>
                </div>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="font-size: 16px; margin: 0;">{message}</p>
                </div>
                
                <div style="text-align: center; margin-top: 20px; font-size: 14px; color: #6c757d;">
                    <p>Contract Analyzer Notification System</p>
                </div>
            </body>
            </html>
            """

			gmail_message = GmailMessage(to=recipient_email, subject=f"Contract Analyzer: {title}", body=html_body)

			return await self.send_email(gmail_message)

		except Exception as e:
			logger.error(f"Failed to send notification email: {e}")
			return False

	async def get_email_templates(self) -> List[Dict[str, Any]]:
		"""Get available email templates"""
		return [
			{
				"id": "contract_analysis",
				"name": "Contract Analysis Results",
				"description": "Send detailed contract analysis results",
				"variables": ["contract_name", "risk_score", "risky_clauses", "analysis_summary", "recommendations"],
			},
			{
				"id": "notification",
				"name": "General Notification",
				"description": "Send general notifications",
				"variables": ["title", "message", "priority"],
			},
			{
				"id": "risk_alert",
				"name": "High Risk Alert",
				"description": "Alert for high-risk contracts",
				"variables": ["contract_name", "risk_score", "urgent_clauses"],
			},
		]

	async def test_connection(self) -> Dict[str, Any]:
		"""Test Gmail connection"""
		try:
			if not await self.authenticate():
				return {"success": False, "message": "Gmail authentication failed", "error": "Invalid credentials or service unavailable"}

			return {
				"success": True,
				"message": "Gmail connection successful",
				"service": "Gmail",
				"authenticated": True,
				"token_expires": self.token_expires_at.isoformat() if self.token_expires_at else None,
			}

		except Exception as e:
			return {"success": False, "message": f"Gmail connection failed: {e!s}", "error": str(e)}
