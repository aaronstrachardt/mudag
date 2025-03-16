"""Module for formatting analysis results in different formats."""

import csv
import json
import os
from typing import Dict, TextIO


def format_table(results: Dict[str, Dict[str, int]], output: TextIO) -> None:
    """
    Format the results as a text table.

    Args:
        results: Dictionary mapping file paths to line count dictionaries
        output: File-like object to write the formatted output to
    """
    # Extract metadata if it exists
    metadata = results.pop("__metadata__", None)

    # Calculate column widths
    path_width = (
        max(len(os.path.relpath(path)) for path in results.keys()) + 2
        if results
        else 10
    )
    path_width = max(path_width, 10)  # Min width for path column

    # Calculate width for index column
    total_files = len(results)
    idx_width = max(len(str(total_files)), 4)  # Minimum of 4 characters for "No."

    # Print summary of analyzed files
    output.write(f"Total files analyzed: {total_files}\n\n")

    # Print header
    header = f"{'No.':<{idx_width}} | {'File Path':<{path_width}} | {'Code':<8} | {'Comment':<8} | {'Blank':<8} | {'Total':<8}"
    separator = "-" * len(header)

    output.write(f"{header}\n")
    output.write(f"{separator}\n")

    # Print data rows
    total_code = 0
    total_comment = 0
    total_blank = 0
    total_lines = 0

    for idx, (path, counts) in enumerate(sorted(results.items()), 1):
        rel_path = os.path.relpath(path)
        code = counts.get("code", 0)
        comment = counts.get("comment", 0)
        blank = counts.get("blank", 0)
        total = counts.get("total", 0)

        total_code += code
        total_comment += comment
        total_blank += blank
        total_lines += total

        output.write(
            f"{idx:<{idx_width}} | {rel_path:<{path_width}} | {code:<8} | {comment:<8} | {blank:<8} | {total:<8}\n"
        )

    # Print separator
    output.write(f"{separator}\n")

    # Print overall total
    output.write(
        f"{'TOTAL':<{idx_width + path_width + 3}} | {total_code:<8} | {total_comment:<8} | {total_blank:<8} | {total_lines:<8}\n"
    )

    # Print workflow language totals if metadata exists
    if metadata and "workflow_languages" in metadata:
        languages = metadata["workflow_languages"]

        # Only print the section if there are files
        if total_files > 0:
            output.write(f"\n\n{'Workflow Language Statistics':}\n")
            output.write(f"{'-' * 40}\n")
            output.write(
                f"{'Language':<15} | {'Files':<8} | {'Code':<8} | {'Comment':<8} | {'Blank':<8} | {'Total':<8}\n"
            )
            output.write(f"{'-' * 70}\n")

            # Print statistics for each language that has files
            for lang, stats in sorted(languages.items()):
                if stats["files"] > 0:
                    output.write(
                        f"{lang:<15} | {stats['files']:<8} | {stats['code']:<8} | {stats['comment']:<8} | {stats['blank']:<8} | {stats['total']:<8}\n"
                    )


def format_json(results: Dict[str, Dict[str, int]], output: TextIO) -> None:
    """
    Format the results as JSON.

    Args:
        results: Dictionary mapping file paths to line count dictionaries
        output: File-like object to write the formatted output to
    """
    # Extract metadata if it exists
    metadata = results.pop("__metadata__", None)

    # Calculate totals
    total_files = len(results)
    total_code = sum(counts.get("code", 0) for counts in results.values())
    total_comment = sum(counts.get("comment", 0) for counts in results.values())
    total_blank = sum(counts.get("blank", 0) for counts in results.values())
    total_lines = total_code + total_comment + total_blank

    # Prepare JSON structure
    output_data = {
        "summary": {
            "total_files": total_files,
            "total_code": total_code,
            "total_comment": total_comment,
            "total_blank": total_blank,
            "total_lines": total_lines,
        },
        "files": {},
    }

    # Add workflow language statistics if available
    if metadata and "workflow_languages" in metadata:
        # Only include languages with files
        language_stats = {
            lang: stats
            for lang, stats in metadata["workflow_languages"].items()
            if stats["files"] > 0
        }
        if language_stats:
            output_data["workflow_languages"] = language_stats

    # Add file data
    for path, counts in results.items():
        rel_path = os.path.relpath(path)
        output_data["files"][rel_path] = counts

    # Write JSON to output
    json.dump(output_data, output, indent=2)


def format_csv(results: Dict[str, Dict[str, int]], output: TextIO) -> None:
    """
    Format the results as CSV.

    Args:
        results: Dictionary mapping file paths to line count dictionaries
        output: File-like object to write the formatted output to
    """
    # Extract metadata if it exists
    metadata = results.pop("__metadata__", None)

    # Initialize CSV writer
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        ["File Path", "Code Lines", "Comment Lines", "Blank Lines", "Total Lines"]
    )

    # Write data rows
    total_code = 0
    total_comment = 0
    total_blank = 0
    total_lines = 0

    for path, counts in sorted(results.items()):
        rel_path = os.path.relpath(path)
        code = counts.get("code", 0)
        comment = counts.get("comment", 0)
        blank = counts.get("blank", 0)
        total = counts.get("total", 0)

        total_code += code
        total_comment += comment
        total_blank += blank
        total_lines += total

        writer.writerow([rel_path, code, comment, blank, total])

    # Write total row
    writer.writerow(["TOTAL", total_code, total_comment, total_blank, total_lines])

    # Write workflow language statistics if available
    if metadata and "workflow_languages" in metadata:
        languages = metadata["workflow_languages"]

        # Only proceed if there are files
        if len(results) > 0:
            # Add a blank row for separation
            writer.writerow([])

            # Add workflow language statistics header
            writer.writerow(
                [
                    "Workflow Language",
                    "Files",
                    "Code Lines",
                    "Comment Lines",
                    "Blank Lines",
                    "Total Lines",
                ]
            )

            # Add data for each language that has files
            for lang, stats in sorted(languages.items()):
                if stats["files"] > 0:
                    writer.writerow(
                        [
                            lang,
                            stats["files"],
                            stats["code"],
                            stats["comment"],
                            stats["blank"],
                            stats["total"],
                        ]
                    )
