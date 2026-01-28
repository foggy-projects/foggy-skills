#!/usr/bin/env python3
"""Docker container management utilities for MySQL client."""

import subprocess
import sys
import os

CONTAINER_NAME = "mysql-client-skill"


def is_container_running():
    """Check if MySQL client container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        return CONTAINER_NAME in result.stdout
    except subprocess.CalledProcessError:
        return False


def is_container_exists():
    """Check if MySQL client container exists (running or stopped)."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        return CONTAINER_NAME in result.stdout
    except subprocess.CalledProcessError:
        return False


def start_container():
    """Start the MySQL client container using docker-compose."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docker_dir = os.path.join(script_dir, "docker")

    if not os.path.exists(os.path.join(docker_dir, "docker-compose.yml")):
        print(f"Error: docker-compose.yml not found in {docker_dir}", file=sys.stderr)
        return False

    try:
        print(f"Starting {CONTAINER_NAME} container...")
        subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=docker_dir,
            check=True,
            capture_output=True
        )
        print(f"[SUCCESS] Container {CONTAINER_NAME} started")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e.stderr.decode()}", file=sys.stderr)
        return False


def ensure_container_running():
    """Ensure the MySQL client container is running, start if needed."""
    if is_container_running():
        return True

    if is_container_exists():
        # Container exists but not running, start it
        try:
            print(f"Starting existing container {CONTAINER_NAME}...")
            subprocess.run(["docker", "start", CONTAINER_NAME], check=True, capture_output=True)
            print(f"[SUCCESS] Container {CONTAINER_NAME} started")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error starting container: {e.stderr.decode()}", file=sys.stderr)
            return False

    # Container doesn't exist, create and start via docker-compose
    return start_container()


def execute_in_container(mysql_args, stdin_data=None):
    """Execute MySQL command in the container.

    Args:
        mysql_args: List of MySQL command arguments (e.g., ['-hhost', '-uuser', ...])
        stdin_data: Optional stdin data to pipe to mysql

    Returns:
        subprocess.CompletedProcess object
    """
    if not ensure_container_running():
        raise RuntimeError("Failed to start MySQL client container")

    docker_cmd = ["docker", "exec"]
    if stdin_data is not None:
        docker_cmd.append("-i")
    docker_cmd.extend([CONTAINER_NAME, "mysql"] + mysql_args)

    return subprocess.run(
        docker_cmd,
        input=stdin_data,
        capture_output=True,
        text=True,
        check=True
    )
