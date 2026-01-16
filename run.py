#!/usr/bin/env python3
"""
Docker Challenge Runner
=======================
Run this script to check your progress.

Usage:
    python run.py          # Check all steps
    python run.py --build  # Build and test the image
"""

import subprocess
import sys
import os
import re
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

if sys.platform == 'win32':
    os.system('color')

CHECKS = [
    {"name": "Dockerfile exists", "points": 5},
    {"name": "Multi-stage build", "points": 15},
    {"name": "Uses slim base image", "points": 10},
    {"name": "Non-root user", "points": 15},
    {"name": "Health check defined", "points": 10},
    {"name": ".dockerignore exists", "points": 5},
    {"name": "docker-compose.yml valid", "points": 15},
    {"name": "Image builds successfully", "points": 10},
    {"name": "Image size < 200MB", "points": 10},
    {"name": "Container runs and responds", "points": 5},
]


def print_header():
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  🐳 Dockerize Python App Challenge{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")


def check_dockerfile_exists():
    """Check if Dockerfile exists."""
    return Path("Dockerfile").exists()


def check_multistage():
    """Check if Dockerfile uses multi-stage build."""
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        # Count FROM statements
        from_count = len(re.findall(r'^FROM\s+', content, re.MULTILINE))
        return from_count >= 2
    except:
        return False


def check_slim_image():
    """Check if final stage uses slim image."""
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        # Find the last FROM statement
        from_statements = re.findall(r'^FROM\s+(\S+)', content, re.MULTILINE)
        if from_statements:
            last_from = from_statements[-1]
            return 'slim' in last_from or 'alpine' in last_from
        return False
    except:
        return False


def check_nonroot_user():
    """Check if Dockerfile creates and uses non-root user."""
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        has_useradd = 'useradd' in content or 'adduser' in content
        has_user = re.search(r'^USER\s+(?!root)', content, re.MULTILINE)
        return has_useradd and has_user
    except:
        return False


def check_healthcheck():
    """Check if Dockerfile defines a health check."""
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        return 'HEALTHCHECK' in content
    except:
        return False


def check_dockerignore():
    """Check if .dockerignore exists and has content."""
    try:
        path = Path(".dockerignore")
        if not path.exists():
            return False
        content = path.read_text()
        # Check for common patterns
        has_pycache = '__pycache__' in content or '*.pyc' in content
        has_venv = 'venv' in content or '.venv' in content
        return has_pycache and has_venv
    except:
        return False


def check_compose_valid():
    """Check if docker-compose.yml is valid."""
    try:
        if not Path("docker-compose.yml").exists():
            return False

        with open("docker-compose.yml", "r") as f:
            content = f.read()

        # Check for required elements
        has_api = 'api:' in content
        has_redis = 'redis:' in content or 'redis:7' in content
        has_ports = '5000:5000' in content

        return has_api and has_ports
    except:
        return False


def check_image_builds():
    """Check if Docker image builds successfully."""
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "docker-challenge-test", "."],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except:
        return False


def check_image_size():
    """Check if image size is under 200MB."""
    try:
        result = subprocess.run(
            ["docker", "images", "docker-challenge-test", "--format", "{{.Size}}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return False, "Image not found"

        size_str = result.stdout.strip()
        # Parse size (e.g., "142MB", "1.2GB")
        if 'GB' in size_str:
            size_mb = float(size_str.replace('GB', '')) * 1024
        elif 'MB' in size_str:
            size_mb = float(size_str.replace('MB', ''))
        else:
            return False, f"Unknown size format: {size_str}"

        return size_mb < 200, f"{size_str}"
    except Exception as e:
        return False, str(e)


def check_container_runs():
    """Check if container runs and responds to health check."""
    try:
        # Stop any existing container
        subprocess.run(["docker", "rm", "-f", "docker-challenge-test-container"],
                      capture_output=True, timeout=10)

        # Run container
        result = subprocess.run(
            ["docker", "run", "-d", "--name", "docker-challenge-test-container",
             "-p", "5001:5000", "docker-challenge-test"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return False

        # Wait for container to start
        import time
        time.sleep(3)

        # Test health endpoint
        import urllib.request
        try:
            response = urllib.request.urlopen("http://localhost:5001/health", timeout=5)
            data = json.loads(response.read())
            success = data.get("status") == "healthy"
        except:
            success = False

        # Cleanup
        subprocess.run(["docker", "rm", "-f", "docker-challenge-test-container"],
                      capture_output=True, timeout=10)

        return success
    except:
        return False


def run_checks():
    """Run all checks and display results."""
    print_header()

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], capture_output=True, timeout=5)
    except:
        print(f"  {Colors.RED}❌ Docker is not installed or not running{Colors.END}")
        print(f"  {Colors.YELLOW}Please install Docker Desktop first{Colors.END}\n")
        return

    results = []
    total_points = 0
    earned_points = 0

    checks_funcs = [
        (check_dockerfile_exists, "Dockerfile exists"),
        (check_multistage, "Multi-stage build"),
        (check_slim_image, "Uses slim base image"),
        (check_nonroot_user, "Non-root user"),
        (check_healthcheck, "Health check defined"),
        (check_dockerignore, ".dockerignore exists"),
        (check_compose_valid, "docker-compose.yml valid"),
    ]

    print(f"  {Colors.BOLD}Checking files...{Colors.END}\n")

    # File checks
    for func, name in checks_funcs:
        check = next(c for c in CHECKS if c["name"] == name)
        total_points += check["points"]

        passed = func()
        if passed:
            earned_points += check["points"]
            print(f"  {Colors.GREEN}✅{Colors.END} {name} ({check['points']} pts)")
        else:
            print(f"  {Colors.RED}❌{Colors.END} {name} (0/{check['points']} pts)")

    # Build check
    print(f"\n  {Colors.BOLD}Building image...{Colors.END}\n")

    build_check = next(c for c in CHECKS if c["name"] == "Image builds successfully")
    total_points += build_check["points"]

    if check_image_builds():
        earned_points += build_check["points"]
        print(f"  {Colors.GREEN}✅{Colors.END} Image builds successfully ({build_check['points']} pts)")

        # Size check
        size_check = next(c for c in CHECKS if c["name"] == "Image size < 200MB")
        total_points += size_check["points"]

        passed, size_info = check_image_size()
        if passed:
            earned_points += size_check["points"]
            print(f"  {Colors.GREEN}✅{Colors.END} Image size < 200MB ({size_info}) ({size_check['points']} pts)")
        else:
            print(f"  {Colors.RED}❌{Colors.END} Image size >= 200MB ({size_info}) (0/{size_check['points']} pts)")

        # Run check
        run_check = next(c for c in CHECKS if c["name"] == "Container runs and responds")
        total_points += run_check["points"]

        print(f"\n  {Colors.BOLD}Testing container...{Colors.END}\n")

        if check_container_runs():
            earned_points += run_check["points"]
            print(f"  {Colors.GREEN}✅{Colors.END} Container runs and responds ({run_check['points']} pts)")
        else:
            print(f"  {Colors.RED}❌{Colors.END} Container doesn't respond (0/{run_check['points']} pts)")
    else:
        print(f"  {Colors.RED}❌{Colors.END} Image build failed (0/{build_check['points']} pts)")
        print(f"  {Colors.YELLOW}   → Fix Dockerfile errors first{Colors.END}")
        total_points += 15  # Add points for size and run checks

    # Summary
    print(f"\n  {Colors.BOLD}Overall Score:{Colors.END}")
    pct = int((earned_points / total_points) * 100) if total_points > 0 else 0
    bar_filled = pct // 5
    bar_empty = 20 - bar_filled

    bar_color = Colors.GREEN if pct >= 80 else Colors.YELLOW if pct >= 50 else Colors.RED
    print(f"  {bar_color}{'█' * bar_filled}{'░' * bar_empty}{Colors.END} {earned_points}/{total_points} pts ({pct}%)")

    if pct == 100:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 CHALLENGE COMPLETE!{Colors.END}")
        print(f"  {Colors.CYAN}You've mastered Docker containerization!{Colors.END}")
    elif pct >= 70:
        print(f"\n  {Colors.YELLOW}Almost there! Check the hints in README.md{Colors.END}")
    else:
        print(f"\n  {Colors.YELLOW}Keep going! See README.md for guidance{Colors.END}")

    print()


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    run_checks()
