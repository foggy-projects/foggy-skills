#!/usr/bin/env python3
"""Execute a single SQL statement via Docker MySQL client."""

import argparse
import sys
from docker_utils import execute_in_container


def execute_sql(host, port, user, password, database, sql, output_format="table"):
    """Execute SQL via Docker MySQL client.

    Args:
        host: MySQL host
        port: MySQL port
        user: MySQL username
        password: MySQL password
        database: Database name
        sql: SQL statement to execute
        output_format: Output format (table, csv, json)

    Returns:
        Exit code (0 for success)
    """
    # Build mysql command arguments
    mysql_args = [
        f"-h{host}",
        f"-P{port}",
        f"-u{user}",
        f"-p{password}",
        database,
        "-e", sql
    ]

    # Add format options
    if output_format == "csv":
        mysql_args.insert(-2, "-B")  # Batch mode
        mysql_args.insert(-2, "--skip-column-names")
    elif output_format == "json":
        mysql_args.insert(-2, "--json")

    try:
        result = execute_in_container(mysql_args)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error executing SQL: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="Execute MySQL SQL via Docker")
    parser.add_argument("--host", required=True, help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--user", required=True, help="MySQL username")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--sql", required=True, help="SQL statement to execute")
    parser.add_argument(
        "--format",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format"
    )

    args = parser.parse_args()

    exit_code = execute_sql(
        args.host,
        args.port,
        args.user,
        args.password,
        args.database,
        args.sql,
        args.format
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
