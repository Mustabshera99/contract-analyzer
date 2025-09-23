#!/usr/bin/env python3
"""
Comprehensive health check script for Contract Analyzer deployment.
Monitors container health, service endpoints, and system resources.
"""

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import docker
import requests


@dataclass
class HealthStatus:
	"""Health status data structure."""

	timestamp: str
	overall_status: str
	services: Dict[str, Any]
	containers: Dict[str, Any]
	system_resources: Dict[str, Any]
	alerts: List[str]


class HealthMonitor:
	"""Comprehensive health monitoring system."""

	def __init__(self, docker_client: Optional[docker.DockerClient] = None):
		"""Initialize the health monitor."""
		self.docker_client = docker_client or docker.from_env()
		self.base_urls = {
			"backend": "http://localhost:8000",
			"frontend": "http://localhost:8501",
			"redis": "http://localhost:6379",
			"nginx": "http://localhost:80",
		}
		self.container_names = ["contract-analyzer-backend", "contract-analyzer-frontend", "contract-analyzer-redis", "contract-analyzer-nginx"]
		self.alerts = []

	def check_container_health(self, container_name: str) -> Dict[str, Any]:
		"""Check individual container health."""
		try:
			container = self.docker_client.containers.get(container_name)

			# Basic container info
			status = container.status
			health_status = container.attrs.get("State", {}).get("Health", {}).get("Status", "unknown")

			# Resource usage
			stats = container.stats(stream=False)
			memory_usage = stats.get("memory_stats", {}).get("usage", 0)
			memory_limit = stats.get("memory_stats", {}).get("limit", 0)
			cpu_usage = self._calculate_cpu_percent(stats)

			# Uptime
			uptime_seconds = self._get_uptime_seconds(container)

			# Health assessment
			is_healthy = status == "running" and health_status in ["healthy", "starting"]

			if not is_healthy:
				self.alerts.append(f"Container {container_name} is not healthy: {status}/{health_status}")

			return {
				"name": container_name,
				"status": status,
				"health_status": health_status,
				"memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
				"memory_limit_mb": round(memory_limit / (1024 * 1024), 2) if memory_limit > 0 else None,
				"memory_percent": round((memory_usage / memory_limit) * 100, 2) if memory_limit > 0 else None,
				"cpu_usage_percent": round(cpu_usage, 2),
				"uptime_seconds": round(uptime_seconds, 2),
				"uptime_human": self._format_uptime(uptime_seconds),
				"is_healthy": is_healthy,
				"restart_count": container.attrs.get("RestartCount", 0),
			}
		except docker.errors.NotFound:
			self.alerts.append(f"Container {container_name} not found")
			return {"name": container_name, "status": "not_found", "is_healthy": False, "error": "Container not found"}
		except Exception as e:
			self.alerts.append(f"Error checking container {container_name}: {e!s}")
			return {"name": container_name, "status": "error", "is_healthy": False, "error": str(e)}

	def check_service_endpoint(self, service_name: str, endpoint: str = "/health") -> Dict[str, Any]:
		"""Check service endpoint health."""
		base_url = self.base_urls.get(service_name)
		if not base_url:
			return {"service": service_name, "is_healthy": False, "error": f"Unknown service: {service_name}"}

		url = f"{base_url}{endpoint}"

		try:
			start_time = time.time()
			response = requests.get(url, timeout=10)
			response_time = (time.time() - start_time) * 1000

			is_healthy = response.status_code == 200

			if not is_healthy:
				self.alerts.append(f"Service {service_name} endpoint returned status {response.status_code}")

			return {
				"service": service_name,
				"url": url,
				"status_code": response.status_code,
				"response_time_ms": round(response_time, 2),
				"is_healthy": is_healthy,
				"response_data": self._parse_response_data(response),
			}
		except requests.exceptions.Timeout:
			self.alerts.append(f"Service {service_name} endpoint timed out")
			return {"service": service_name, "url": url, "is_healthy": False, "error": "Request timeout"}
		except requests.exceptions.ConnectionError:
			self.alerts.append(f"Service {service_name} endpoint connection refused")
			return {"service": service_name, "url": url, "is_healthy": False, "error": "Connection refused"}
		except Exception as e:
			self.alerts.append(f"Error checking service {service_name}: {e!s}")
			return {"service": service_name, "url": url, "is_healthy": False, "error": str(e)}

	def check_system_resources(self) -> Dict[str, Any]:
		"""Check system resource usage."""
		try:
			# Get Docker system info
			system_info = self.docker_client.info()

			# Calculate resource usage
			total_memory = system_info.get("MemTotal", 0)
			used_memory = system_info.get("MemUsed", 0)
			memory_percent = (used_memory / total_memory) * 100 if total_memory > 0 else 0

			# Check disk usage
			disk_usage = self.docker_client.df()
			total_space = sum(volume.get("Size", 0) for volume in disk_usage.get("Volumes", []))
			used_space = sum(volume.get("Size", 0) for volume in disk_usage.get("Volumes", []) if volume.get("Size", 0) > 0)
			disk_percent = (used_space / total_space) * 100 if total_space > 0 else 0

			# Check for resource warnings
			if memory_percent > 80:
				self.alerts.append(f"High memory usage: {memory_percent:.1f}%")
			if disk_percent > 80:
				self.alerts.append(f"High disk usage: {disk_percent:.1f}%")

			return {
				"memory_total_gb": round(total_memory / (1024**3), 2),
				"memory_used_gb": round(used_memory / (1024**3), 2),
				"memory_percent": round(memory_percent, 2),
				"disk_total_gb": round(total_space / (1024**3), 2),
				"disk_used_gb": round(used_space / (1024**3), 2),
				"disk_percent": round(disk_percent, 2),
				"docker_version": system_info.get("ServerVersion", "unknown"),
				"containers_running": system_info.get("ContainersRunning", 0),
				"containers_stopped": system_info.get("ContainersStopped", 0),
			}
		except Exception as e:
			self.alerts.append(f"Error checking system resources: {e!s}")
			return {"error": str(e), "is_healthy": False}

	def check_security_headers(self) -> Dict[str, Any]:
		"""Check security headers on services."""
		security_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", "Strict-Transport-Security", "Content-Security-Policy"]

		results = {}

		for service_name in ["backend", "frontend"]:
			base_url = self.base_urls.get(service_name)
			if not base_url:
				continue

			try:
				response = requests.get(base_url, timeout=5)
				headers = response.headers

				service_headers = {}
				for header in security_headers:
					service_headers[header] = headers.get(header, "Not set")

				results[service_name] = {
					"status_code": response.status_code,
					"headers": service_headers,
					"has_security_headers": any(service_headers[header] != "Not set" for header in security_headers),
				}
			except Exception as e:
				results[service_name] = {"error": str(e), "has_security_headers": False}

		return results

	def run_comprehensive_check(self) -> HealthStatus:
		"""Run comprehensive health check."""
		self.alerts = []  # Reset alerts

		# Check all containers
		containers = {}
		for container_name in self.container_names:
			containers[container_name] = self.check_container_health(container_name)

		# Check all service endpoints
		services = {}
		for service_name in ["backend", "frontend"]:
			services[service_name] = self.check_service_endpoint(service_name)

		# Check Redis
		services["redis"] = self.check_service_endpoint("redis", "/ping")

		# Check system resources
		system_resources = self.check_system_resources()

		# Check security headers
		security_headers = self.check_security_headers()
		services["security_headers"] = security_headers

		# Determine overall status
		all_containers_healthy = all(container.get("is_healthy", False) for container in containers.values())
		all_services_healthy = all(service.get("is_healthy", False) for service in services.values() if service.get("is_healthy") is not None)

		if all_containers_healthy and all_services_healthy and not self.alerts:
			overall_status = "healthy"
		elif len(self.alerts) <= 2:
			overall_status = "warning"
		else:
			overall_status = "critical"

		return HealthStatus(
			timestamp=datetime.now().isoformat(),
			overall_status=overall_status,
			services=services,
			containers=containers,
			system_resources=system_resources,
			alerts=self.alerts,
		)

	def _calculate_cpu_percent(self, stats: Dict) -> float:
		"""Calculate CPU usage percentage from Docker stats."""
		try:
			cpu_delta = stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
			system_delta = stats.get("cpu_stats", {}).get("system_cpu_usage", 0)
			cpu_count = len(stats.get("cpu_stats", {}).get("cpu_usage", {}).get("percpu_usage", []))

			if system_delta > 0 and cpu_delta > 0:
				return (cpu_delta / system_delta) * cpu_count * 100.0
			return 0.0
		except (KeyError, ZeroDivisionError):
			return 0.0

	def _get_uptime_seconds(self, container) -> float:
		"""Get container uptime in seconds."""
		try:
			started_at = container.attrs.get("State", {}).get("StartedAt")
			if started_at:
				from datetime import datetime

				start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
				return (datetime.now(start_time.tzinfo) - start_time).total_seconds()
			return 0.0
		except Exception:
			return 0.0

	def _format_uptime(self, seconds: float) -> str:
		"""Format uptime in human-readable format."""
		if seconds < 60:
			return f"{int(seconds)}s"
		elif seconds < 3600:
			return f"{int(seconds // 60)}m {int(seconds % 60)}s"
		elif seconds < 86400:
			hours = int(seconds // 3600)
			minutes = int((seconds % 3600) // 60)
			return f"{hours}h {minutes}m"
		else:
			days = int(seconds // 86400)
			hours = int((seconds % 86400) // 3600)
			return f"{days}d {hours}h"

	def _parse_response_data(self, response) -> Any:
		"""Parse response data based on content type."""
		content_type = response.headers.get("content-type", "")

		if "application/json" in content_type:
			try:
				return response.json()
			except:
				return response.text[:200]
		else:
			return response.text[:200]


def print_health_status(status: HealthStatus, format_type: str = "human"):
	"""Print health status in specified format."""
	if format_type == "json":
		print(json.dumps(asdict(status), indent=2))
		return

	# Human-readable format
	print(f"\n{'=' * 60}")
	print(f"Contract Analyzer Health Check - {status.timestamp}")
	print(f"{'=' * 60}")

	# Overall status
	status_color = {
		"healthy": "\033[92m",  # Green
		"warning": "\033[93m",  # Yellow
		"critical": "\033[91m",  # Red
	}.get(status.overall_status, "\033[0m")

	print(f"\nOverall Status: {status_color}{status.overall_status.upper()}\033[0m")

	# Alerts
	if status.alerts:
		print(f"\n\033[91mALERTS:\033[0m")
		for alert in status.alerts:
			print(f"  • {alert}")

	# Container status
	print(f"\n\033[94mCONTAINERS:\033[0m")
	for container_name, container_info in status.containers.items():
		health_icon = "✓" if container_info.get("is_healthy", False) else "✗"
		status_color = "\033[92m" if container_info.get("is_healthy", False) else "\033[91m"

		print(f"  {health_icon} {container_name}")
		print(f"    Status: {status_color}{container_info.get('status', 'unknown')}\033[0m")
		print(f"    Health: {container_info.get('health_status', 'unknown')}")
		print(f"    Memory: {container_info.get('memory_usage_mb', 0)}MB")
		print(f"    CPU: {container_info.get('cpu_usage_percent', 0)}%")
		print(f"    Uptime: {container_info.get('uptime_human', 'unknown')}")
		if container_info.get("restart_count", 0) > 0:
			print(f"    Restarts: {container_info.get('restart_count', 0)}")
		print()

	# Service status
	print(f"\n\033[94mSERVICES:\033[0m")
	for service_name, service_info in status.services.items():
		if service_name == "security_headers":
			continue

		health_icon = "✓" if service_info.get("is_healthy", False) else "✗"
		status_color = "\033[92m" if service_info.get("is_healthy", False) else "\033[91m"

		print(f"  {health_icon} {service_name}")
		print(f"    URL: {service_info.get('url', 'N/A')}")
		print(f"    Status: {status_color}{service_info.get('status_code', 'N/A')}\033[0m")
		print(f"    Response Time: {service_info.get('response_time_ms', 0)}ms")
		if service_info.get("error"):
			print(f"    Error: {service_info.get('error')}")
		print()

	# System resources
	if status.system_resources and not status.system_resources.get("error"):
		print(f"\n\033[94mSYSTEM RESOURCES:\033[0m")
		print(
			f"  Memory: {status.system_resources.get('memory_used_gb', 0)}GB / {status.system_resources.get('memory_total_gb', 0)}GB ({status.system_resources.get('memory_percent', 0)}%)"
		)
		print(
			f"  Disk: {status.system_resources.get('disk_used_gb', 0)}GB / {status.system_resources.get('disk_total_gb', 0)}GB ({status.system_resources.get('disk_percent', 0)}%)"
		)
		print(
			f"  Containers: {status.system_resources.get('containers_running', 0)} running, {status.system_resources.get('containers_stopped', 0)} stopped"
		)
		print()


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(description="Contract Analyzer Health Check")
	parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
	parser.add_argument("--watch", "-w", action="store_true", help="Watch mode (continuous monitoring)")
	parser.add_argument("--interval", "-i", type=int, default=30, help="Watch interval in seconds")
	parser.add_argument("--exit-on-error", action="store_true", help="Exit with error code if unhealthy")

	args = parser.parse_args()

	try:
		monitor = HealthMonitor()

		if args.watch:
			print(f"Starting health monitoring (interval: {args.interval}s). Press Ctrl+C to stop.")
			try:
				while True:
					status = monitor.run_comprehensive_check()
					print_health_status(status, args.format)

					if args.exit_on_error and status.overall_status == "critical":
						print("\nExiting due to critical health status.")
						sys.exit(1)

					time.sleep(args.interval)
			except KeyboardInterrupt:
				print("\nHealth monitoring stopped.")
		else:
			status = monitor.run_comprehensive_check()
			print_health_status(status, args.format)

			if args.exit_on_error and status.overall_status == "critical":
				sys.exit(1)

	except Exception as e:
		print(f"Error running health check: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()
