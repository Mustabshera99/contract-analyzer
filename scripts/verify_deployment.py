#!/usr/bin/env python3
"""
Contract Risk Analyzer Deployment Verification Script

This script performs comprehensive verification of the Contract Risk Analyzer
deployment, including health checks, functionality tests, and performance validation.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

import httpx
import requests
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


class DeploymentVerifier:
    """Comprehensive deployment verification tool."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "warnings": 0}
        }
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    def log_test(self, name: str, status: str, message: str = "", details: Dict = None):
        """Log test result."""
        test_result = {
            "name": name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.results["tests"].append(test_result)
        self.results["summary"][status] += 1
        
        # Color-coded console output
        if status == "passed":
            print(f"{Fore.GREEN}✅ {name}: {message}")
        elif status == "failed":
            print(f"{Fore.RED}❌ {name}: {message}")
        elif status == "warnings":
            print(f"{Fore.YELLOW}⚠️  {name}: {message}")
        else:
            print(f"{Fore.BLUE}ℹ️  {name}: {message}")
    
    async def verify_connectivity(self) -> bool:
        """Verify basic connectivity to the API."""
        print(f"\n{Fore.CYAN}🔍 Testing API Connectivity...")
        
        try:
            response = await self.client.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "API Connectivity",
                    "passed",
                    f"API is reachable (status: {data.get('status', 'unknown')})",
                    {"status_code": response.status_code, "response_data": data}
                )
                return True
            else:
                self.log_test(
                    "API Connectivity",
                    "failed",
                    f"API returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
        except Exception as e:
            self.log_test(
                "API Connectivity",
                "failed",
                f"Failed to connect to API: {e}",
                {"error": str(e)}
            )
            return False
    
    async def verify_health_endpoints(self) -> None:
        """Verify all health check endpoints."""
        print(f"\n{Fore.CYAN}🏥 Testing Health Endpoints...")
        
        endpoints = [
            ("/health", "Basic Health Check"),
            ("/health/detailed", "Detailed Health Check"),
            ("/health/readiness", "Readiness Check"),
            ("/health/liveness", "Liveness Check")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = await self.client.get(f"{self.api_base}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        name,
                        "passed",
                        f"Endpoint responding correctly",
                        {"status_code": response.status_code, "endpoint": endpoint}
                    )
                else:
                    self.log_test(
                        name,
                        "failed",
                        f"Endpoint returned status {response.status_code}",
                        {"status_code": response.status_code, "endpoint": endpoint}
                    )
            except Exception as e:
                self.log_test(
                    name,
                    "failed",
                    f"Endpoint failed: {e}",
                    {"error": str(e), "endpoint": endpoint}
                )
    
    async def verify_api_documentation(self) -> None:
        """Verify API documentation is available."""
        print(f"\n{Fore.CYAN}📚 Testing API Documentation...")
        
        # Test OpenAPI schema
        try:
            response = await self.client.get(f"{self.base_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "openapi" in data and "paths" in data:
                    self.log_test(
                        "OpenAPI Schema",
                        "passed",
                        f"OpenAPI schema available with {len(data.get('paths', {}))} endpoints",
                        {"endpoint_count": len(data.get('paths', {}))}
                    )
                else:
                    self.log_test(
                        "OpenAPI Schema",
                        "failed",
                        "OpenAPI schema is malformed",
                        {"response_data": data}
                    )
            else:
                self.log_test(
                    "OpenAPI Schema",
                    "failed",
                    f"OpenAPI schema returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "OpenAPI Schema",
                "failed",
                f"OpenAPI schema failed: {e}",
                {"error": str(e)}
            )
        
        # Test Swagger UI
        try:
            response = await self.client.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log_test(
                    "Swagger UI",
                    "passed",
                    "Swagger UI is available",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Swagger UI",
                    "warnings",
                    f"Swagger UI returned status {response.status_code} (may be disabled in production)",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "Swagger UI",
                "warnings",
                f"Swagger UI failed: {e}",
                {"error": str(e)}
            )
    
    async def verify_file_upload_validation(self) -> None:
        """Verify file upload validation."""
        print(f"\n{Fore.CYAN}📁 Testing File Upload Validation...")
        
        # Test with no file
        try:
            response = await self.client.post(f"{self.api_base}/analyze-contract")
            if response.status_code == 422:
                self.log_test(
                    "No File Validation",
                    "passed",
                    "Correctly rejects requests without files",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "No File Validation",
                    "failed",
                    f"Expected 422, got {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "No File Validation",
                "failed",
                f"Request failed: {e}",
                {"error": str(e)}
            )
        
        # Test with invalid file type
        try:
            files = {'file': ('test.txt', b'This is not a PDF', 'text/plain')}
            response = await self.client.post(f"{self.api_base}/analyze-contract", files=files)
            if response.status_code == 415:
                self.log_test(
                    "Invalid File Type Validation",
                    "passed",
                    "Correctly rejects invalid file types",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Invalid File Type Validation",
                    "failed",
                    f"Expected 415, got {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "Invalid File Type Validation",
                "failed",
                f"Request failed: {e}",
                {"error": str(e)}
            )
    
    async def verify_synchronous_analysis(self) -> None:
        """Verify synchronous contract analysis."""
        print(f"\n{Fore.CYAN}🔄 Testing Synchronous Analysis...")
        
        # Create a test PDF
        test_pdf = self._create_test_pdf()
        
        try:
            files = {'file': ('test_contract.pdf', test_pdf, 'application/pdf')}
            start_time = time.time()
            response = await self.client.post(f"{self.api_base}/analyze-contract", files=files)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                required_fields = ["risky_clauses", "suggested_redlines", "email_draft", "status"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if not missing_fields:
                    self.log_test(
                        "Synchronous Analysis",
                        "passed",
                        f"Analysis completed in {processing_time:.2f}s",
                        {
                            "processing_time": processing_time,
                            "risky_clauses_count": len(result.get("risky_clauses", [])),
                            "redlines_count": len(result.get("suggested_redlines", [])),
                            "risk_score": result.get("overall_risk_score")
                        }
                    )
                else:
                    self.log_test(
                        "Synchronous Analysis",
                        "failed",
                        f"Missing required fields: {missing_fields}",
                        {"missing_fields": missing_fields, "response_data": result}
                    )
            else:
                error_text = response.text
                self.log_test(
                    "Synchronous Analysis",
                    "failed",
                    f"Analysis failed with status {response.status_code}",
                    {"status_code": response.status_code, "error": error_text}
                )
        except Exception as e:
            self.log_test(
                "Synchronous Analysis",
                "failed",
                f"Analysis request failed: {e}",
                {"error": str(e)}
            )
    
    async def verify_asynchronous_analysis(self) -> None:
        """Verify asynchronous contract analysis."""
        print(f"\n{Fore.CYAN}🔄 Testing Asynchronous Analysis...")
        
        # Create a test PDF
        test_pdf = self._create_test_pdf()
        
        try:
            # Start async analysis
            files = {
                'file': ('test_contract.pdf', test_pdf, 'application/pdf'),
                'timeout_seconds': (None, '60'),
                'priority': (None, 'normal'),
            }
            response = await self.client.post(f"{self.api_base}/analyze-contract/async", files=files)
            if response.status_code == 202:
                task_info = response.json()
                task_id = task_info.get("task_id")
                
                if task_id:
                    self.log_test(
                        "Async Analysis Start",
                        "passed",
                        f"Analysis task started: {task_id}",
                        {"task_id": task_id, "status": task_info.get("status")}
                    )
                    
                    # Monitor progress
                    await self._monitor_async_analysis(task_id)
                else:
                    self.log_test(
                        "Async Analysis Start",
                        "failed",
                        "No task ID returned",
                        {"response_data": task_info}
                    )
            else:
                error_text = response.text
                self.log_test(
                    "Async Analysis Start",
                    "failed",
                    f"Failed to start analysis: {response.status_code}",
                    {"status_code": response.status_code, "error": error_text}
                )
        except Exception as e:
            self.log_test(
                "Async Analysis Start",
                "failed",
                f"Async analysis request failed: {e}",
                {"error": str(e)}
            )
    
    async def _monitor_async_analysis(self, task_id: str) -> None:
        """Monitor async analysis progress."""
        max_wait = 30  # 30 seconds max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = await self.client.get(f"{self.api_base}/analyze-contract/async/{task_id}/status")
                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get("status")
                    
                    if current_status in ["completed", "failed", "timeout"]:
                        if current_status == "completed":
                            # Get results
                            result_response = await self.client.get(f"{self.api_base}/analyze-contract/async/{task_id}/result")
                            if result_response.status_code == 200:
                                result = result_response.json()
                                self.log_test(
                                    "Async Analysis Completion",
                                    "passed",
                                    f"Analysis completed successfully",
                                    {
                                        "task_id": task_id,
                                        "risky_clauses_count": len(result.get("risky_clauses", [])),
                                        "redlines_count": len(result.get("suggested_redlines", [])),
                                        "risk_score": result.get("overall_risk_score")
                                    }
                                )
                            else:
                                self.log_test(
                                    "Async Analysis Completion",
                                    "failed",
                                    f"Failed to get results: {result_response.status_code}",
                                    {"status_code": result_response.status_code}
                                )
                        else:
                            self.log_test(
                                "Async Analysis Completion",
                                "failed",
                                f"Analysis {current_status}",
                                {"task_id": task_id, "status": current_status}
                            )
                        break
                    else:
                        # Still running, wait a bit
                        await asyncio.sleep(2)
                else:
                    self.log_test(
                        "Async Analysis Monitoring",
                        "failed",
                        f"Status check failed: {response.status_code}",
                        {"status_code": response.status_code}
                    )
                    break
            except Exception as e:
                self.log_test(
                    "Async Analysis Monitoring",
                    "failed",
                    f"Monitoring failed: {e}",
                    {"error": str(e)}
                )
                break
        else:
            self.log_test(
                "Async Analysis Monitoring",
                "warnings",
                f"Analysis did not complete within {max_wait} seconds",
                {"task_id": task_id, "timeout": max_wait}
            )
    
    async def verify_service_metrics(self) -> None:
        """Verify service metrics endpoint."""
        print(f"\n{Fore.CYAN}📊 Testing Service Metrics...")
        
        try:
            response = await self.client.get(f"{self.api_base}/analyze-contract/service/metrics")
            if response.status_code == 200:
                metrics = response.json()
                
                required_metrics = ["total_tasks", "active_tasks", "completed_tasks", "failed_tasks"]
                missing_metrics = [metric for metric in required_metrics if metric not in metrics]
                
                if not missing_metrics:
                    self.log_test(
                        "Service Metrics",
                        "passed",
                        f"Metrics available with {len(metrics)} data points",
                        {"metrics_count": len(metrics), "metrics": metrics}
                    )
                else:
                    self.log_test(
                        "Service Metrics",
                        "failed",
                        f"Missing required metrics: {missing_metrics}",
                        {"missing_metrics": missing_metrics, "available_metrics": list(metrics.keys())}
                    )
            else:
                self.log_test(
                    "Service Metrics",
                    "failed",
                    f"Metrics endpoint returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "Service Metrics",
                "failed",
                f"Metrics request failed: {e}",
                {"error": str(e)}
            )
    
    async def verify_websocket_endpoints(self) -> None:
        """Verify WebSocket endpoints."""
        print(f"\n{Fore.CYAN}🔌 Testing WebSocket Endpoints...")
        
        try:
            response = await self.client.get(f"{self.api_base}/ws/stats")
            if response.status_code == 200:
                stats = response.json()
                
                required_fields = ["total_connections", "active_tasks"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_test(
                        "WebSocket Stats",
                        "passed",
                        f"WebSocket stats available",
                        {"stats": stats}
                    )
                else:
                    self.log_test(
                        "WebSocket Stats",
                        "failed",
                        f"Missing required fields: {missing_fields}",
                        {"missing_fields": missing_fields, "available_fields": list(stats.keys())}
                    )
            else:
                self.log_test(
                    "WebSocket Stats",
                    "failed",
                    f"WebSocket stats returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "WebSocket Stats",
                "failed",
                f"WebSocket stats request failed: {e}",
                {"error": str(e)}
            )
    
    async def verify_error_handling(self) -> None:
        """Verify error handling."""
        print(f"\n{Fore.CYAN}❌ Testing Error Handling...")
        
        # Test invalid task ID
        try:
            response = await self.client.get(f"{self.api_base}/analyze-contract/async/invalid_task_id/status")
            if response.status_code == 404:
                self.log_test(
                    "Invalid Task ID Handling",
                    "passed",
                    "Correctly returns 404 for invalid task ID",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Invalid Task ID Handling",
                    "failed",
                    f"Expected 404, got {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "Invalid Task ID Handling",
                "failed",
                f"Request failed: {e}",
                {"error": str(e)}
            )
        
        # Test cancel invalid task
        try:
            response = await self.client.delete(f"{self.api_base}/analyze-contract/async/invalid_task_id")
            if response.status_code == 404:
                self.log_test(
                    "Cancel Invalid Task Handling",
                    "passed",
                    "Correctly returns 404 for canceling invalid task",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Cancel Invalid Task Handling",
                    "failed",
                    f"Expected 404, got {response.status_code}",
                    {"status_code": response.status_code}
                )
        except Exception as e:
            self.log_test(
                "Cancel Invalid Task Handling",
                "failed",
                f"Request failed: {e}",
                {"error": str(e)}
            )
    
    async def verify_performance(self) -> None:
        """Verify performance benchmarks."""
        print(f"\n{Fore.CYAN}⚡ Testing Performance...")
        
        # Test health check response time
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.api_base}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 1.0:
                self.log_test(
                    "Health Check Performance",
                    "passed",
                    f"Health check responded in {response_time:.3f}s",
                    {"response_time": response_time}
                )
            elif response.status_code == 200:
                self.log_test(
                    "Health Check Performance",
                    "warnings",
                    f"Health check slow: {response_time:.3f}s (expected < 1.0s)",
                    {"response_time": response_time}
                )
            else:
                self.log_test(
                    "Health Check Performance",
                    "failed",
                    f"Health check failed with status {response.status_code}",
                    {"status_code": response.status_code, "response_time": response_time}
                )
        except Exception as e:
            self.log_test(
                "Health Check Performance",
                "failed",
                f"Health check request failed: {e}",
                {"error": str(e)}
            )
    
    def _create_test_pdf(self) -> bytes:
        """Create a minimal test PDF for testing."""
        # This is a minimal PDF content for testing
        test_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 100
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Contract for Analysis) Tj
0 -20 Td
(This is a sample contract for testing purposes.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
353
%%EOF"""
        return test_content
    
    def generate_report(self, output_file: str = None) -> None:
        """Generate verification report."""
        if not output_file:
            output_file = f"deployment_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n{Fore.GREEN}📄 Report saved to: {output_file}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Failed to save report: {e}")
    
    def print_summary(self) -> None:
        """Print verification summary."""
        summary = self.results["summary"]
        total_tests = sum(summary.values())
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}DEPLOYMENT VERIFICATION SUMMARY")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}✅ Passed: {summary['passed']}")
        print(f"{Fore.RED}❌ Failed: {summary['failed']}")
        print(f"{Fore.YELLOW}⚠️  Warnings: {summary['warnings']}")
        print(f"{Fore.BLUE}📊 Total Tests: {total_tests}")
        
        if summary['failed'] == 0:
            print(f"\n{Fore.GREEN}🎉 All critical tests passed! Deployment is ready.")
        else:
            print(f"\n{Fore.RED}❌ {summary['failed']} critical tests failed. Please review and fix issues.")
        
        if summary['warnings'] > 0:
            print(f"\n{Fore.YELLOW}⚠️  {summary['warnings']} warnings found. Consider reviewing these items.")


async def main():
    """Main verification function."""
    print(f"{Fore.CYAN}🚀 Contract Risk Analyzer Deployment Verification")
    print(f"{Fore.CYAN}{'='*60}")
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print(f"{Fore.BLUE}🔗 Testing API at: {base_url}")
    
    async with DeploymentVerifier(base_url) as verifier:
        # Run all verification tests
        await verifier.verify_connectivity()
        await verifier.verify_health_endpoints()
        await verifier.verify_api_documentation()
        await verifier.verify_file_upload_validation()
        await verifier.verify_synchronous_analysis()
        await verifier.verify_asynchronous_analysis()
        await verifier.verify_service_metrics()
        await verifier.verify_websocket_endpoints()
        await verifier.verify_error_handling()
        await verifier.verify_performance()
        
        # Generate report and summary
        verifier.generate_report()
        verifier.print_summary()
        
        # Exit with appropriate code
        if verifier.results["summary"]["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())