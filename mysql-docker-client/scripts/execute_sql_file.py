#!/usr/bin/env python3
"""Execute SQL file via Docker MySQL client."""

import argparse
import sys
import os
from docker_utils import execute_in_container


def execute_sql_file(host, port, user, password, database, sql_file):
    """Execute SQL file via Docker MySQL client.

    Args:
        host: MySQL host
        port: MySQL port
        user: MySQL username
        password: MySQL password
        database: Database name
        sql_file: Path to SQL file

    Returns:
        Exit code (0 for success)
    """
    if not os.path.exists(sql_file):
        print(f"Error: SQL file not found: {sql_file}", file=sys.stderr)
        return 1

    # Build mysql command arguments
    mysql_args = [
        f"-h{host}",
        f"-P{port}",
        f"-u{user}",
        f"-p{password}",
        database
    ]

    try:
        # Read SQL file and pipe to container
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        result = execute_in_container(mysql_args, stdin_data=sql_content)

        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        print(f"[SUCCESS] Successfully executed SQL file: {sql_file}")
        return 0
    except Exception as e:
        print(f"Error executing SQL file: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="Execute MySQL SQL file via Docker")
    parser.add_argument("--host", required=True, help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--user", required=True, help="MySQL username")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--file", required=True, help="SQL file to execute")

    args = parser.parse_args()

    exit_code = execute_sql_file(
        args.host,
        args.port,
        args.user,
        args.password,
        args.database,
        args.file
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
