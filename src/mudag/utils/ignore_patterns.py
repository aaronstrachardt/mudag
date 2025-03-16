"""Module for handling ignore patterns (similar to .gitignore)."""

import os
import fnmatch
from pathlib import Path
from typing import List, Pattern


class IgnorePatterns:
    """Class for handling ignore patterns."""

    def __init__(self) -> None:
        """
        Initialize ignore patterns from .mudagignore files.
        Automatically looks for .mudagignore in the current directory and user's home directory.
        """
        self.patterns: List[str] = []
        self._regex_patterns: List[Pattern] = []

        # Look for .mudagignore in the current directory
        current_dir_ignore = ".mudagignore"
        if os.path.isfile(current_dir_ignore):
            self._load_ignore_file(current_dir_ignore)

        # Look for global .mudagignore in user's home directory
        home_dir = Path.home()
        global_ignore = os.path.join(home_dir, ".mudagignore")
        if os.path.isfile(global_ignore):
            self._load_ignore_file(global_ignore)

    def _load_ignore_file(self, ignore_file: str) -> None:
        """
        Load ignore patterns from a file.

        Args:
            ignore_file: Path to the ignore file
        """
        try:
            with open(ignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        self.patterns.append(line)

                        # We'll handle the pattern matching in is_ignored method
                        # Store the raw pattern for now
                        self._regex_patterns.append(line)
        except (IOError, UnicodeDecodeError) as e:
            print(f"Error reading ignore file {ignore_file}: {e}")

    def is_ignored(self, path: str) -> bool:
        """
        Check if a path matches any ignore pattern.

        Args:
            path: Path to check (either absolute or relative)

        Returns:
            True if the path should be ignored, False otherwise
        """
        # Always use normalized path
        path = os.path.normpath(path)

        # Check each pattern
        for pattern in self.patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith("/"):
                dir_name = pattern[:-1]  # Remove the trailing slash

                # Check if path is the directory or is inside this directory
                # Need to handle both "dir/" and "path/to/dir/"
                if (
                    path == dir_name  # Exact match
                    or path.startswith(
                        f"{dir_name}/"
                    )  # Path is inside this directory directly
                    or f"/{dir_name}/" in f"/{path}/"  # Path contains this directory
                    or path.endswith(f"/{dir_name}")
                ):  # Path ends with this directory
                    return True
            else:
                # Regular file pattern
                # Check against the full path and the basename
                basename = os.path.basename(path)

                # Use fnmatch for glob-style matching
                if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(basename, pattern):
                    return True

        return False
