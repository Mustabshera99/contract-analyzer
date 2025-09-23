#!/usr/bin/env python3
"""
Script to run the Contract Analyzer application locally without Docker.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def run_backend():
	"""Run the backend server."""
	print("🚀 Starting backend server...")
	backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
	return subprocess.Popen(backend_cmd)


def run_frontend():
	"""Run the frontend server."""
	print("🚀 Starting frontend server...")
	frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
	return subprocess.Popen(frontend_cmd)


def main():
	"""Main function to run both servers."""
	print("🔒 Contract Risk Analyzer - Local Development Setup")
	print("=" * 50)

	# Change to project directory
	project_dir = Path(__file__).parent
	os.chdir(project_dir)

	# Check if virtual environment exists
	venv_path = project_dir / "venv"
	if not venv_path.exists():
		print("❌ Virtual environment not found. Please run: python -m venv venv")
		sys.exit(1)

	# Activate virtual environment
	if sys.platform == "win32":
		activate_script = venv_path / "Scripts" / "activate.bat"
		python_exe = venv_path / "Scripts" / "python.exe"
	else:
		activate_script = venv_path / "bin" / "activate"
		python_exe = venv_path / "bin" / "python"

	if not python_exe.exists():
		print("❌ Python executable not found in virtual environment")
		sys.exit(1)

	# Update sys.executable to use venv python
	sys.executable = str(python_exe)

	processes = []

	try:
		# Start backend
		backend_process = run_backend()
		processes.append(backend_process)

		# Wait a bit for backend to start
		print("⏳ Waiting for backend to start...")
		time.sleep(3)

		# Start frontend
		frontend_process = run_frontend()
		processes.append(frontend_process)

		print("\n✅ Both servers are starting up!")
		print("📊 Backend API: http://localhost:8000")
		print("📊 API Docs: http://localhost:8000/docs")
		print("🌐 Frontend UI: http://localhost:8501")
		print("\nPress Ctrl+C to stop both servers")

		# Wait for processes
		for process in processes:
			process.wait()

	except KeyboardInterrupt:
		print("\n🛑 Shutting down servers...")
		for process in processes:
			process.terminate()
		print("✅ Servers stopped successfully")
	except Exception as e:
		print(f"❌ Error: {e}")
		for process in processes:
			process.terminate()
		sys.exit(1)


if __name__ == "__main__":
	main()
