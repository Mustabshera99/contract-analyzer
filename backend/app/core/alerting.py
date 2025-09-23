"""
Alerting and Notification System
"""

import json
import logging
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
	"""Alert severity levels"""

	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"
	CRITICAL = "critical"


class AlertStatus(Enum):
	"""Alert status"""

	ACTIVE = "active"
	ACKNOWLEDGED = "acknowledged"
	RESOLVED = "resolved"
	SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
	"""Alert rule definition"""

	name: str
	condition: str  # Metric name and threshold
	severity: AlertSeverity
	enabled: bool = True
	cooldown_minutes: int = 5
	last_triggered: Optional[datetime] = None

	def should_trigger(self, current_time: datetime) -> bool:
		"""Check if alert should trigger based on cooldown"""
		if not self.enabled:
			return False

		if self.last_triggered is None:
			return True

		cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
		return current_time >= cooldown_end


@dataclass
class Alert:
	"""Alert instance"""

	id: str
	rule_name: str
	severity: AlertSeverity
	message: str
	details: Dict[str, Any]
	timestamp: datetime
	status: AlertStatus = AlertStatus.ACTIVE
	resolved_at: Optional[datetime] = None
	acknowledged_by: Optional[str] = None
	acknowledged_at: Optional[datetime] = None


class AlertManager:
	"""Manages alerts and notifications"""

	def __init__(self):
		self.rules: Dict[str, AlertRule] = {}
		self.active_alerts: Dict[str, Alert] = {}
		self.alert_history: List[Alert] = []
		self.notification_handlers: List[Callable[[Alert], None]] = []

	def add_rule(self, rule: AlertRule):
		"""Add an alert rule"""
		self.rules[rule.name] = rule

	def add_notification_handler(self, handler: Callable[[Alert], None]):
		"""Add a notification handler"""
		self.notification_handlers.append(handler)

	def check_metrics(self, metrics: Dict[str, Any]):
		"""Check metrics against alert rules"""
		current_time = datetime.now(timezone.utc)

		for rule_name, rule in self.rules.items():
			if not rule.should_trigger(current_time):
				continue

			# Simple condition parsing (can be enhanced)
			if self._evaluate_condition(rule.condition, metrics):
				self._trigger_alert(rule, metrics, current_time)

	def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
		"""Evaluate alert condition"""
		try:
			# Simple threshold evaluation
			# Format: "metric_name > threshold" or "metric_name < threshold"
			parts = condition.split()
			if len(parts) != 3:
				return False

			metric_name, operator, threshold_str = parts
			threshold = float(threshold_str)
			metric_value = metrics.get(metric_name, 0)

			if operator == ">":
				return metric_value > threshold
			elif operator == "<":
				return metric_value < threshold
			elif operator == ">=":
				return metric_value >= threshold
			elif operator == "<=":
				return metric_value <= threshold
			elif operator == "==":
				return metric_value == threshold
			elif operator == "!=":
				return metric_value != threshold

			return False
		except (ValueError, KeyError):
			return False

	def _trigger_alert(self, rule: AlertRule, metrics: Dict[str, Any], timestamp: datetime):
		"""Trigger an alert"""
		alert_id = f"{rule.name}_{int(timestamp.timestamp())}"

		alert = Alert(
			id=alert_id,
			rule_name=rule.name,
			severity=rule.severity,
			message=f"Alert triggered: {rule.name}",
			details={"condition": rule.condition, "metrics": metrics, "threshold": rule.condition.split()[-1]},
			timestamp=timestamp,
		)

		self.active_alerts[alert_id] = alert
		self.alert_history.append(alert)
		rule.last_triggered = timestamp

		# Send notifications
		for handler in self.notification_handlers:
			try:
				handler(alert)
			except Exception as e:
				logger.error(f"Error in notification handler: {e}")

	def acknowledge_alert(self, alert_id: str, user: str):
		"""Acknowledge an alert"""
		if alert_id in self.active_alerts:
			alert = self.active_alerts[alert_id]
			alert.status = AlertStatus.ACKNOWLEDGED
			alert.acknowledged_by = user
			alert.acknowledged_at = datetime.now(timezone.utc)

	def resolve_alert(self, alert_id: str, user: str = None):
		"""Resolve an alert"""
		if alert_id in self.active_alerts:
			alert = self.active_alerts[alert_id]
			alert.status = AlertStatus.RESOLVED
			alert.resolved_at = datetime.now(timezone.utc)
			if user:
				alert.acknowledged_by = user

	def get_active_alerts(self) -> List[Alert]:
		"""Get all active alerts"""
		return [alert for alert in self.active_alerts.values() if alert.status == AlertStatus.ACTIVE]

	def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
		"""Get alerts by severity"""
		return [alert for alert in self.active_alerts.values() if alert.severity == severity]


class EmailNotifier:
	"""Email notification handler"""

	def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
		self.smtp_server = smtp_server
		self.smtp_port = smtp_port
		self.username = username
		self.password = password
		self.from_email = from_email
		self.to_emails: List[str] = []

	def add_recipient(self, email: str):
		"""Add email recipient"""
		self.to_emails.append(email)

	def __call__(self, alert: Alert):
		"""Send email notification"""
		if not self.to_emails:
			return

		subject = f"[{alert.severity.value.upper()}] {alert.message}"
		body = self._format_alert_email(alert)

		try:
			with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
				server.starttls()
				server.login(self.username, self.password)

				for to_email in self.to_emails:
					message = f"To: {to_email}\nFrom: {self.from_email}\nSubject: {subject}\n\n{body}"
					server.sendmail(self.from_email, to_email, message)

			logger.info(f"Alert email sent for {alert.id}")
		except Exception as e:
			logger.error(f"Failed to send alert email: {e}")

	def _format_alert_email(self, alert: Alert) -> str:
		"""Format alert for email"""
		return f"""
Alert Details:
- ID: {alert.id}
- Rule: {alert.rule_name}
- Severity: {alert.severity.value.upper()}
- Time: {alert.timestamp.isoformat()}
- Message: {alert.message}

Details:
{json.dumps(alert.details, indent=2)}

Please check the monitoring dashboard for more information.
"""


class SlackNotifier:
	"""Slack notification handler"""

	def __init__(self, webhook_url: str, channel: str = None):
		self.webhook_url = webhook_url
		self.channel = channel

	def __call__(self, alert: Alert):
		"""Send Slack notification"""
		import requests

		payload = {
			"text": f"🚨 Alert: {alert.message}",
			"attachments": [
				{
					"color": self._get_color(alert.severity),
					"fields": [
						{"title": "Severity", "value": alert.severity.value.upper(), "short": True},
						{"title": "Rule", "value": alert.rule_name, "short": True},
						{"title": "Time", "value": alert.timestamp.isoformat(), "short": True},
						{"title": "Details", "value": json.dumps(alert.details, indent=2), "short": False},
					],
				}
			],
		}

		if self.channel:
			payload["channel"] = self.channel

		try:
			response = requests.post(self.webhook_url, json=payload)
			response.raise_for_status()
			logger.info(f"Slack notification sent for alert {alert.id}")
		except Exception as e:
			logger.error(f"Failed to send Slack notification: {e}")

	def _get_color(self, severity: AlertSeverity) -> str:
		"""Get color for alert severity"""
		colors = {AlertSeverity.LOW: "good", AlertSeverity.MEDIUM: "warning", AlertSeverity.HIGH: "danger", AlertSeverity.CRITICAL: "#8B0000"}
		return colors.get(severity, "good")


class LogNotifier:
	"""Log-based notification handler"""

	def __init__(self, logger_name: str = "alerts"):
		self.logger = logging.getLogger(logger_name)

	def __call__(self, alert: Alert):
		"""Log alert"""
		self.logger.warning(
			f"ALERT: {alert.severity.value.upper()} - {alert.message} | Rule: {alert.rule_name} | Details: {json.dumps(alert.details)}"
		)


# Create global alert manager
alert_manager = AlertManager()

# Add default log notifier
alert_manager.add_notification_handler(LogNotifier())


# Convenience functions
def add_alert_rule(name: str, condition: str, severity: AlertSeverity, cooldown_minutes: int = 5):
	"""Add an alert rule"""
	rule = AlertRule(name=name, condition=condition, severity=severity, cooldown_minutes=cooldown_minutes)
	alert_manager.add_rule(rule)


def check_alerts(metrics: Dict[str, Any]):
	"""Check metrics against alert rules"""
	alert_manager.check_metrics(metrics)
