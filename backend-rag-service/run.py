#!/usr/bin/env python
import os
import subprocess
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


def run_api_service():
    """Run the API service"""
    print("Starting API service on port 8000...")
    subprocess.run([sys.executable, "-m", "api_service.run"])


def run_embedder_service():
    """Run the embedder service"""
    print("Starting embedder service on port 8001...")
    subprocess.run([sys.executable, "-m", "embedder_service.run"])


def run_all_services():
    """Run all services in parallel using Docker Compose"""
    print("Starting all services using Docker Compose...")

    # Check if docker-compose command is available
    docker_compose_cmd = "docker-compose"
    try:
        subprocess.run(
            [docker_compose_cmd, "--version"], check=True, capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try the newer docker compose command
        docker_compose_cmd = "docker compose"

    # Build and start services
    compose_command = f"{docker_compose_cmd} up --build"
    print(f"Running: {compose_command}")
    os.system(compose_command)  # Using os.system to keep process attached


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG services")
    parser.add_argument(
        "--service",
        choices=["api", "embedder", "all"],
        default="all",
        help="Which service to run (default: all)",
    )

    args = parser.parse_args()

    if args.service == "api":
        run_api_service()
    elif args.service == "embedder":
        run_embedder_service()
    else:
        run_all_services()
