"""Main CLI module for the Mudag tool."""

import argparse
import logging
import os
import sys

from ..core.analyzer import count_lines, is_workflow_file, scan_directory
from ..utils.formatter import format_csv, format_json, format_table
from ..utils.ignore_patterns import IgnorePatterns
from ..utils.logging_utils import setup_logger


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="mudag",
        description="A tool for analyzing research software repositories with focus on workflow languages.",
        epilog="Example: mudag analyze path/to/repo --format json --output results.json",
    )

    # Add common arguments
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument("--log-file", help="Path to the log file")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # Add 'analyze' command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze a file or directory"
    )
    analyze_parser.add_argument("path", help="Path to the file or directory to analyze")
    analyze_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format",
    )
    analyze_parser.add_argument("--output", help="Output file path (default: stdout)")

    # Add 'list-workflows' command
    list_parser = subparsers.add_parser(
        "list-workflows", help="List workflow files in a directory"
    )
    list_parser.add_argument("path", help="Path to the directory to scan")

    return parser.parse_args()


def analyze_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Execute the 'analyze' command.

    Args:
        args: Parsed command-line arguments
        logger: Logger instance

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    path = args.path
    output_path = args.output
    output_format = args.format

    logger.info(f"Analyzing workflow files in {path}")

    if os.path.isdir(path):
        results = scan_directory(path)
    elif os.path.isfile(path):
        if not is_workflow_file(path):
            logger.warning(f"{path} is not a workflow file, skipping")
            return 0
        results = {path: count_lines(path)}
    else:
        logger.error(f"{path} does not exist")
        return 1

    # Open output file or use stdout
    output_file = sys.stdout
    if output_path:
        try:
            output_file = open(output_path, "w", encoding="utf-8")
        except IOError as e:
            logger.error(f"Error opening output file {output_path}: {e}")
            return 1

    try:
        # Format and output results
        if output_format == "table":
            format_table(results, output_file)
        elif output_format == "json":
            format_json(results, output_file)
        elif output_format == "csv":
            format_csv(results, output_file)
    finally:
        if output_file is not sys.stdout:
            output_file.close()

    return 0


def list_workflows_command(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Execute the 'list-workflows' command.

    Args:
        args: Parsed command-line arguments
        logger: Logger instance

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    path = args.path

    logger.info(f"Listing workflow files in {path}")

    if not os.path.isdir(path):
        logger.error(f"{path} is not a directory")
        return 1

    # Initialize ignore patterns
    ignore_patterns = IgnorePatterns()

    # Collect all workflow files
    workflow_files = []
    for root, dirs, files in os.walk(path):
        # Skip directories that match ignore patterns
        dirs[:] = [
            d for d in dirs if not ignore_patterns.is_ignored(os.path.join(root, d))
        ]

        for file in files:
            full_path = os.path.join(root, file)

            # Skip files that match ignore patterns
            if ignore_patterns.is_ignored(full_path):
                continue

            if is_workflow_file(full_path):
                # Use relative path from the scanned directory
                rel_path = os.path.relpath(full_path, path)
                workflow_files.append(rel_path)

    # Print sorted list of workflow files
    for file in sorted(workflow_files):
        print(file)

    logger.info(f"Found {len(workflow_files)} workflow files")
    return 0


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()

    # Set up logging
    logger = setup_logger(args.log_level, args.log_file)

    # Execute the requested command
    try:
        if args.command == "analyze":
            return analyze_command(args, logger)
        elif args.command == "list-workflows":
            return list_workflows_command(args, logger)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
