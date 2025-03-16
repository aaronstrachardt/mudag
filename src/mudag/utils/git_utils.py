"""Module for git-related operations."""

import os
import subprocess
import tempfile
from typing import Dict, List, Optional

from ..core.analyzer import count_lines, is_workflow_file


def is_git_repo(directory: str) -> bool:
    """
    Check if a directory is a git repository.

    Args:
        directory: Path to the directory to check

    Returns:
        True if the directory is a git repository, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "-C", directory, "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_file_from_commit(
    repo_path: str, commit_hash: str, file_path: str
) -> Optional[str]:
    """
    Get the content of a file from a specific commit.

    Args:
        repo_path: Path to the git repository
        commit_hash: Git commit hash
        file_path: Path to the file relative to the repository root

    Returns:
        Content of the file at the given commit, or None if the file doesn't exist
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "show", f"{commit_hash}:{file_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except subprocess.SubprocessError:
        return None


def get_files_at_commit(
    repo_path: str, commit_hash: str, workflow_only: bool = True
) -> List[str]:
    """
    Get the list of files at a specific commit.

    Args:
        repo_path: Path to the git repository
        commit_hash: Git commit hash
        workflow_only: If True, only include workflow language files

    Returns:
        List of file paths relative to the repository root
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "ls-tree", "-r", "--name-only", commit_hash],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            files = result.stdout.strip().split("\n")
            if workflow_only:
                files = [f for f in files if is_workflow_file(f)]
            return files
        return []
    except subprocess.SubprocessError:
        return []


def compare_commits(
    repo_path: str,
    commit1: str,
    commit2: str,
    exclude_dirs: Optional[List[str]] = None,
    workflow_only: bool = True,
) -> Dict[str, Dict[str, int]]:
    """
    Compare line counts between two git commits.

    Args:
        repo_path: Path to the git repository
        commit1: First git commit hash
        commit2: Second git commit hash
        exclude_dirs: List of directory names to exclude
        workflow_only: If True, only analyze workflow language files

    Returns:
        Dictionary with differences in line counts between the two commits
    """
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", "node_modules", "venv", "env"]

    # Check if the path is a git repository
    if not is_git_repo(repo_path):
        raise ValueError(f"{repo_path} is not a git repository")

    # Get files at both commits
    files1 = get_files_at_commit(repo_path, commit1, workflow_only)
    files2 = get_files_at_commit(repo_path, commit2, workflow_only)

    # Filter excluded directories
    files1 = [f for f in files1 if not any(d in f.split(os.sep) for d in exclude_dirs)]
    files2 = [f for f in files2 if not any(d in f.split(os.sep) for d in exclude_dirs)]

    # Get all unique files
    all_files = set(files1) | set(files2)

    results = {}

    # Compare each file
    for file_path in all_files:
        # Get file content at both commits
        content1 = get_file_from_commit(repo_path, commit1, file_path)
        content2 = get_file_from_commit(repo_path, commit2, file_path)

        # Count lines in temporary files
        counts1 = {}
        counts2 = {}

        if content1 is not None:
            with tempfile.NamedTemporaryFile("w", delete=False) as temp1:
                temp1.write(content1)
                temp1_path = temp1.name

            try:
                counts1 = count_lines(temp1_path)
            finally:
                os.unlink(temp1_path)

        if content2 is not None:
            with tempfile.NamedTemporaryFile("w", delete=False) as temp2:
                temp2.write(content2)
                temp2_path = temp2.name

            try:
                counts2 = count_lines(temp2_path)
            finally:
                os.unlink(temp2_path)

        # Calculate differences
        diff = {
            "code": counts2.get("code", 0) - counts1.get("code", 0),
            "comment": counts2.get("comment", 0) - counts1.get("comment", 0),
            "blank": counts2.get("blank", 0) - counts1.get("blank", 0),
            "total": counts2.get("total", 0) - counts1.get("total", 0),
            "commit1": {
                "code": counts1.get("code", 0),
                "comment": counts1.get("comment", 0),
                "blank": counts1.get("blank", 0),
                "total": counts1.get("total", 0),
            },
            "commit2": {
                "code": counts2.get("code", 0),
                "comment": counts2.get("comment", 0),
                "blank": counts2.get("blank", 0),
                "total": counts2.get("total", 0),
            },
        }

        # Only include files with differences
        if diff["total"] != 0:
            results[file_path] = diff

    return results
