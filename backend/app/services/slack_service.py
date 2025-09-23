"""
Enhanced Slack integration service for contract analysis notifications
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class SlackMessage(BaseModel):
	"""Slack message model"""

	text: str
	channel: Optional[str] = None
	username: Optional[str] = None
	icon_emoji: Optional[str] = None
	attachments: Optional[List[Dict[str, Any]]] = None
	blocks: Optional[List[Dict[str, Any]]] = None


class SlackAttachment(BaseModel):
	"""Slack attachment model"""

	color: str = "good"  # good, warning, danger, or hex color
	title: str
	text: str
	fields: Optional[List[Dict[str, str]]] = None
	footer: Optional[str] = None
	ts: Optional[int] = None


class SlackService:
	"""Enhanced Slack integration service"""

	def __init__(self):
		self.settings = get_settings()
		self.webhook_url = getattr(self.settings, "slack_webhook_url", "")
		self.bot_token = getattr(self.settings, "slack_bot_token", "")
		self.default_channel = getattr(self.settings, "slack_default_channel", "#contracts")
		self.enabled = getattr(self.settings, "slack_enabled", False)

		self.base_url = "https://slack.com/api"

		logger.info(f"Slack service initialized: enabled={self.enabled}")

	async def send_message(self, message: SlackMessage) -> bool:
		"""Send a message to Slack"""
		try:
			if not self.enabled:
				logger.warning("Slack not enabled")
				return False

			if not self.webhook_url and not self.bot_token:
				logger.warning("No Slack webhook URL or bot token configured")
				return False

			# Use webhook if available, otherwise use bot token
			if self.webhook_url:
				return await self._send_via_webhook(message)
			else:
				return await self._send_via_bot(message)

		except Exception as e:
			logger.error(f"Failed to send Slack message: {e}")
			return False

	async def _send_via_webhook(self, message: SlackMessage) -> bool:
		"""Send message via Slack webhook"""
		try:
			payload = {
				"text": message.text,
				"channel": message.channel or self.default_channel,
				"username": message.username or "Contract Analyzer",
				"icon_emoji": message.icon_emoji or ":page_with_curl:",
			}

			if message.attachments:
				payload["attachments"] = message.attachments

			if message.blocks:
				payload["blocks"] = message.blocks

			async with httpx.AsyncClient() as client:
				response = await client.post(self.webhook_url, json=payload)
				return response.status_code == 200

		except Exception as e:
			logger.error(f"Failed to send Slack webhook: {e}")
			return False

	async def _send_via_bot(self, message: SlackMessage) -> bool:
		"""Send message via Slack bot API"""
		try:
			headers = {"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json"}

			payload = {"channel": message.channel or self.default_channel, "text": message.text}

			if message.attachments:
				payload["attachments"] = message.attachments

			if message.blocks:
				payload["blocks"] = message.blocks

			async with httpx.AsyncClient() as client:
				response = await client.post(f"{self.base_url}/chat.postMessage", headers=headers, json=payload)
				result = response.json()
				return result.get("ok", False)

		except Exception as e:
			logger.error(f"Failed to send Slack bot message: {e}")
			return False

	async def send_contract_analysis_alert(
		self, contract_name: str, risk_score: float, risky_clauses: List[Dict[str, Any]], analysis_summary: str, analysis_url: Optional[str] = None
	) -> bool:
		"""Send contract analysis alert to Slack"""
		try:
			# Determine risk level and color
			if risk_score >= 7:
				risk_level = "High"
				color = "danger"
				emoji = "🔴"
			elif risk_score >= 4:
				risk_level = "Medium"
				color = "warning"
				emoji = "🟡"
			else:
				risk_level = "Low"
				color = "good"
				emoji = "🟢"

			# Create main message
			main_text = f"{emoji} *Contract Analysis Complete*"

			# Create attachment with details
			attachment = {
				"color": color,
				"title": f"Contract: {contract_name}",
				"text": analysis_summary,
				"fields": [
					{"title": "Risk Score", "value": f"{risk_score}/10 ({risk_level})", "short": True},
					{"title": "Risky Clauses", "value": str(len(risky_clauses)), "short": True},
					{"title": "Analysis Date", "value": datetime.now().strftime("%Y-%m-%d %H:%M"), "short": True},
				],
				"footer": "Contract Analyzer AI",
				"ts": int(datetime.now().timestamp()),
			}

			# Add risky clauses if any
			if risky_clauses:
				clause_text = ""
				for i, clause in enumerate(risky_clauses[:3], 1):  # Show top 3
					clause_text += f"• *{clause.get('risk_level', 'Unknown')} Risk*: {clause.get('clause_text', '')[:100]}...\n"

				if len(risky_clauses) > 3:
					clause_text += f"... and {len(risky_clauses) - 3} more clauses"

				attachment["fields"].append({"title": "Key Risk Areas", "value": clause_text, "short": False})

			# Add analysis URL if provided
			if analysis_url:
				attachment["actions"] = [{"type": "button", "text": "View Full Analysis", "url": analysis_url}]

			message = SlackMessage(text=main_text, channel="#contracts", attachments=[attachment])

			return await self.send_message(message)

		except Exception as e:
			logger.error(f"Failed to send contract analysis alert: {e}")
			return False

	async def send_risk_alert(self, contract_name: str, risk_score: float, urgent_clauses: List[Dict[str, Any]]) -> bool:
		"""Send high-risk alert to Slack"""
		try:
			main_text = f"🚨 *HIGH RISK CONTRACT ALERT*"

			attachment = {
				"color": "danger",
				"title": f"Urgent Review Required: {contract_name}",
				"text": f"Risk Score: {risk_score}/10 - Immediate legal review recommended",
				"fields": [
					{"title": "Contract Name", "value": contract_name, "short": True},
					{"title": "Risk Score", "value": f"{risk_score}/10", "short": True},
					{"title": "Urgent Clauses", "value": str(len(urgent_clauses)), "short": True},
				],
				"footer": "Contract Analyzer AI - High Risk Alert",
				"ts": int(datetime.now().timestamp()),
			}

			# Add urgent clauses
			if urgent_clauses:
				clause_text = ""
				for clause in urgent_clauses[:5]:  # Show top 5 urgent clauses
					clause_text += f"• *{clause.get('risk_level', 'Unknown')}*: {clause.get('clause_text', '')[:80]}...\n"

				attachment["fields"].append({"title": "Critical Issues", "value": clause_text, "short": False})

			message = SlackMessage(text=main_text, channel="#legal-alerts", attachments=[attachment])

			return await self.send_message(message)

		except Exception as e:
			logger.error(f"Failed to send risk alert: {e}")
			return False

	async def send_daily_summary(self, total_contracts: int, high_risk_count: int, medium_risk_count: int, low_risk_count: int) -> bool:
		"""Send daily analysis summary to Slack"""
		try:
			main_text = f"📊 *Daily Contract Analysis Summary*"

			attachment = {
				"color": "good",
				"title": f"Analysis Summary - {datetime.now().strftime('%Y-%m-%d')}",
				"text": f"Processed {total_contracts} contracts today",
				"fields": [
					{"title": "High Risk", "value": f"{high_risk_count} contracts", "short": True},
					{"title": "Medium Risk", "value": f"{medium_risk_count} contracts", "short": True},
					{"title": "Low Risk", "value": f"{low_risk_count} contracts", "short": True},
				],
				"footer": "Contract Analyzer AI - Daily Report",
				"ts": int(datetime.now().timestamp()),
			}

			message = SlackMessage(text=main_text, channel="#daily-reports", attachments=[attachment])

			return await self.send_message(message)

		except Exception as e:
			logger.error(f"Failed to send daily summary: {e}")
			return False

	async def send_notification(self, title: str, message: str, priority: str = "normal", channel: Optional[str] = None) -> bool:
		"""Send a general notification to Slack"""
		try:
			# Priority emojis and colors
			priority_config = {
				"high": {"emoji": "🔴", "color": "danger"},
				"medium": {"emoji": "🟡", "color": "warning"},
				"normal": {"emoji": "ℹ️", "color": "good"},
				"low": {"emoji": "✅", "color": "good"},
			}

			config = priority_config.get(priority.lower(), priority_config["normal"])

			main_text = f"{config['emoji']} *{title}*"

			attachment = {"color": config["color"], "text": message, "footer": "Contract Analyzer AI", "ts": int(datetime.now().timestamp())}

			slack_message = SlackMessage(text=main_text, channel=channel or self.default_channel, attachments=[attachment])

			return await self.send_message(slack_message)

		except Exception as e:
			logger.error(f"Failed to send notification: {e}")
			return False

	async def test_connection(self) -> Dict[str, Any]:
		"""Test Slack connection"""
		try:
			if not self.enabled:
				return {"success": False, "message": "Slack not enabled", "error": "Service disabled"}

			if not self.webhook_url and not self.bot_token:
				return {"success": False, "message": "No Slack credentials configured", "error": "Missing webhook URL or bot token"}

			# Test with a simple message
			test_message = SlackMessage(text="🧪 Contract Analyzer connection test", channel=self.default_channel)

			success = await self.send_message(test_message)

			return {
				"success": success,
				"message": "Slack connection test completed",
				"service": "Slack",
				"method": "webhook" if self.webhook_url else "bot",
				"channel": self.default_channel,
			}

		except Exception as e:
			return {"success": False, "message": f"Slack connection test failed: {e!s}", "error": str(e)}

	async def get_channels(self) -> List[Dict[str, str]]:
		"""Get available Slack channels (requires bot token)"""
		try:
			if not self.bot_token:
				return []

			headers = {"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json"}

			async with httpx.AsyncClient() as client:
				response = await client.get(f"{self.base_url}/conversations.list", headers=headers)
				result = response.json()

					if result.get("ok"):
						channels = []
						for channel in result.get("channels", []):
							if not channel.get("is_archived"):
								channels.append({"id": channel["id"], "name": channel["name"], "is_private": channel.get("is_private", False)})
						return channels

					return []

		except Exception as e:
			logger.error(f"Failed to get Slack channels: {e}")
			return []
