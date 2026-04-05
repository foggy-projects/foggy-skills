#!/usr/bin/env python3
"""Export MySQL query results to file via Docker client."""

import argparse
import sys
import os
from docker_utils import execute_in_container


def export_data(host, port, user, password, database, sql, output_file, output_format="csv"):
    """Export query results to file.

    Args:
        host: MySQL host
        port: MySQL port
        user: MySQL username
        password: MySQL password
        database: Database name
        sql: SQL query
        output_file: Output file path
        output_format: Output format (csv or json)

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
    elif output_format == "json":
        mysql_args.insert(-2, "--json")

    try:
        result = execute_in_container(mysql_args)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        print(f"[SUCCESS] Data exported to: {output_file}")
        print(f"  Format: {output_format}")
        print(f"  Size: {os.path.getsize(output_file)} bytes")

        return 0
    except Exception as e:
        print(f"Error exporting data: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="Export MySQL data via Docker")
    parser.add_argument("--host", required=True, help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--user", required=True, help="MySQL username")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--sql", required=True, help="SQL query to execute")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format"
    )

    args = parser.parse_args()

    exit_code = export_data(
        args.host,
        args.port,
        args.user,
        args.password,
        args.database,
        args.sql,
        args.output,
        args.format
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
