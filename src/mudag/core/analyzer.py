"""Module for analyzing files and counting lines."""

import os
import re
from typing import Dict, List, Optional, Set

from ..utils.ignore_patterns import IgnorePatterns


def is_workflow_file(file_path: str) -> bool:
    """
    Check if a file is a workflow language file.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file is a workflow language file, False otherwise
    """
    # Define workflow languages and their extensions
    workflow_languages = {
        "Galaxy": [".ga", ".galaxy", ".gxwf"],
        "Common Workflow Language": [".cwl"],
        "Nextflow": [".nf", ".nextflow", ".config"],
        "Snakemake": [
            "Snakefile",
            "snakefile",
            "SNAKEFILE",
            "Snake",
            "snake",
            ".smk",
            ".snake",
            ".snakefile",
            ".snakemake",
            ".rules",
            ".rule",
        ],
        "KNIME": [".knwf", ".workflow.knime", ".knar"],
        "WDL": [".wdl"],
    }

    # Flatten the extensions into a single set
    workflow_extensions: Set[str] = set()
    for extensions in workflow_languages.values():
        workflow_extensions.update([ext.lower() for ext in extensions])

    # Check file basename for exact matches (like "Snakefile")
    basename = os.path.basename(file_path)
    basename_lower = basename.lower()

    # Handle special case for .workflow.knime
    if basename_lower.endswith(".workflow.knime"):
        return True

    # Explicitly exclude yaml files (they may be part of workflows but not workflow languages themselves)
    _, ext = os.path.splitext(file_path.lower())
    if ext in [".yml", ".yaml"]:
        return False

    if basename_lower in workflow_extensions:
        return True

    # Check if the file follows special Snakemake patterns like "Snakefile.py" or "Snakefile_main"
    if basename_lower.startswith("snakefile") or basename_lower.startswith("snake"):
        return True

    # Additional check for numeric suffixes like snake_1, snake_2, etc.
    if re.match(r"snakefile[\._-]\d+", basename_lower) or re.match(
        r"snake[\._-]\d+", basename_lower
    ):
        return True

    # Check file extension
    return ext in workflow_extensions


def count_lines(file_path: str) -> Dict[str, int]:
    """
    Count the number of code, comment, and blank lines in a file.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dictionary with counts for 'code', 'comment', and 'blank' lines
    """
    code_lines = 0
    comment_lines = 0
    blank_lines = 0

    # Get file extension and basename
    basename = os.path.basename(file_path)
    basename_lower = basename.lower()
    _, ext = os.path.splitext(file_path.lower())

    # Define comment markers for different file types
    if (
        ext in [".py", ".smk", ".snake", ".snakefile", ".snakemake", ".rules", ".rule"]
        or basename_lower in ["snakefile", "snake"]
        or basename_lower.startswith("snakefile")
        or basename_lower.startswith("snake")
    ):
        # Python and Snakemake
        line_comment = "#"
        block_starts = ['"""', "'''"]
        block_ends = ['"""', "'''"]
    elif ext in [".cwl", ".ga", ".galaxy", ".gxwf", ".wdl"] or ext in [".yml", ".yaml"]:
        # YAML-based formats (including .yml and .yaml, even though they're not considered workflow files)
        line_comment = "#"
        block_starts = None
        block_ends = None
    elif ext in [".nf", ".nextflow", ".config"]:
        # Nextflow
        line_comment = "//"
        block_starts = ["/*"]
        block_ends = ["*/"]
    elif ext in [".knwf", ".workflow.knime", ".knar"] or basename_lower.endswith(
        ".workflow.knime"
    ):
        # KNIME (XML-based)
        line_comment = "<!--"
        block_starts = ["<!--"]
        block_ends = ["-->"]
    else:
        # Default to Python-like comments if file type is unknown
        line_comment = "#"
        block_starts = ['"""', "'''"]
        block_ends = ['"""', "'''"]

    in_block_comment = False
    current_block_end = None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

            i = 0
            while i < len(lines):
                line = lines[i].rstrip()

                # Handle blank lines
                if not line.strip():
                    blank_lines += 1
                    i += 1
                    continue

                # Handle block comments
                if in_block_comment:
                    comment_lines += 1
                    if current_block_end and (current_block_end in line):
                        in_block_comment = False
                        current_block_end = None
                    i += 1
                    continue

                # Check for start of block comments
                if block_starts:
                    started_block = False
                    for j, block_start in enumerate(block_starts):
                        if line.strip().startswith(block_start):
                            comment_lines += 1
                            if (
                                block_ends[j]
                                not in line[line.find(block_start) + len(block_start) :]
                            ):
                                in_block_comment = True
                                current_block_end = block_ends[j]
                            started_block = True
                            break
                    if started_block:
                        i += 1
                        continue

                # Handle line comments
                if line.strip().startswith(line_comment):
                    comment_lines += 1
                else:
                    code_lines += 1

                i += 1
    except (UnicodeDecodeError, IOError) as e:
        print(f"Error reading file {file_path}: {e}")
        return {"code": 0, "comment": 0, "blank": 0, "error": 1}

    return {
        "code": code_lines,
        "comment": comment_lines,
        "blank": blank_lines,
        "total": code_lines + comment_lines + blank_lines,
    }


def get_workflow_language(file_path: str) -> str:
    """
    Determine the workflow language of a file.

    Args:
        file_path: Path to the file to check

    Returns:
        String identifying the workflow language (e.g., "Snakemake", "CWL")
    """
    # Get file extension and basename
    basename = os.path.basename(file_path)
    basename_lower = basename.lower()
    _, ext = os.path.splitext(file_path.lower())

    # Check for .workflow.knime special case
    if basename_lower.endswith(".workflow.knime"):
        return "KNIME"

    # Check for Snakemake
    if (
        ext in [".smk", ".snake", ".snakefile", ".snakemake", ".rules", ".rule"]
        or basename_lower in ["snakefile", "snake"]
        or basename_lower.startswith("snakefile")
        or basename_lower.startswith("snake")
    ):
        return "Snakemake"

    # Check for CWL
    if ext == ".cwl":
        return "CWL"

    # Check for Nextflow
    if ext in [".nf", ".nextflow", ".config"]:
        return "Nextflow"

    # Check for Galaxy
    if ext in [".ga", ".galaxy", ".gxwf"]:
        return "Galaxy"

    # Check for KNIME
    if ext in [".knwf", ".knar"]:
        return "KNIME"

    # Check for WDL
    if ext == ".wdl":
        return "WDL"

    # Default to "Other" if not recognized
    return "Other"


def scan_directory(directory: str) -> Dict[str, Dict[str, int]]:
    """
    Scan a directory and count lines in workflow language files.

    Args:
        directory: Path to the directory to scan

    Returns:
        Dictionary mapping file paths to line count dictionaries
    """
    # Initialize ignore patterns
    ignore_patterns = IgnorePatterns()

    results = {}

    # Add metadata to track file categories
    results["__metadata__"] = {
        "workflow_languages": {
            "Snakemake": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
            "CWL": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
            "Nextflow": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
            "Galaxy": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
            "KNIME": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
            "WDL": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
            "Other": {"files": 0, "code": 0, "comment": 0, "blank": 0, "total": 0},
        }
    }

    for root, dirs, files in os.walk(directory):
        # Exclude directories that match ignore patterns
        dirs[:] = [
            d for d in dirs if not ignore_patterns.is_ignored(os.path.join(root, d))
        ]

        for file in files:
            file_path = os.path.join(root, file)

            # Skip files that match ignore patterns
            if ignore_patterns.is_ignored(file_path):
                continue

            if not is_workflow_file(file_path):
                continue

            # Count lines in the file
            line_counts = count_lines(file_path)
            results[file_path] = line_counts

            # Determine workflow language and update metadata
            language = get_workflow_language(file_path)
            results["__metadata__"]["workflow_languages"][language]["files"] += 1
            results["__metadata__"]["workflow_languages"][language]["code"] += (
                line_counts["code"]
            )
            results["__metadata__"]["workflow_languages"][language]["comment"] += (
                line_counts["comment"]
            )
            results["__metadata__"]["workflow_languages"][language]["blank"] += (
                line_counts["blank"]
            )
            results["__metadata__"]["workflow_languages"][language]["total"] += (
                line_counts["total"]
            )

    return results


def compare_versions(
    directory: str,
    git_commit1: str,
    git_commit2: str,
    exclude_dirs: Optional[List[str]] = None,
    workflow_only: bool = True,
) -> Dict[str, Dict[str, int]]:
    """
    Compare line counts between two git commits.

    Args:
        directory: Path to the git repository
        git_commit1: First git commit hash
        git_commit2: Second git commit hash
        exclude_dirs: List of directory names to exclude
        workflow_only: If True, only analyze workflow language files

    Returns:
        Dictionary with differences in line counts between the two commits
    """
    # This is a placeholder for the git comparison functionality
    # It would require implementing git operations to checkout different commits
    # and compare the files between them

    # For now, just return an empty dictionary
    return {}
