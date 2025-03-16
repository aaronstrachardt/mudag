"""Unit tests for the ignore_patterns module."""

import os
import tempfile


from mudag.utils.ignore_patterns import IgnorePatterns


def test_ignore_patterns_initialization() -> None:
    """Test initialization of IgnorePatterns with no .mudagignore file present."""
    patterns = IgnorePatterns()
    assert len(patterns.patterns) == 0
    assert len(patterns._regex_patterns) == 0


def test_ignore_patterns_with_local_file() -> None:
    """Test IgnorePatterns with a local .mudagignore file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .mudagignore file in the temp directory
        with open(os.path.join(temp_dir, ".mudagignore"), "w") as mudagignore:
            mudagignore.write("""# Test ignore file
*.log
temp/
test_data.txt
""")

        # Change to the temp directory to test .mudagignore auto-detection
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Initialize IgnorePatterns, which should auto-detect the .mudagignore file
            patterns = IgnorePatterns()

            # Verify patterns were loaded
            assert len(patterns.patterns) == 3
            assert patterns.patterns == ["*.log", "temp/", "test_data.txt"]

            # Test pattern matching
            assert patterns.is_ignored("file.log") is True
            assert patterns.is_ignored("logs/error.log") is True
            assert patterns.is_ignored("temp/file.txt") is True
            assert patterns.is_ignored("dir/temp/file.txt") is True
            assert patterns.is_ignored("test_data.txt") is True
            assert patterns.is_ignored("dir/test_data.txt") is True

            # Test non-matching paths
            assert patterns.is_ignored("file.txt") is False
            assert patterns.is_ignored("logfile") is False
            assert patterns.is_ignored("temporal/file.txt") is False
        finally:
            # Change back to the original directory
            os.chdir(original_dir)


def test_ignore_patterns_empty_lines_and_comments() -> None:
    """Test that empty lines and comments are properly ignored."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .mudagignore file with empty lines and comments
        with open(os.path.join(temp_dir, ".mudagignore"), "w") as mudagignore:
            mudagignore.write("""# Test ignore file with comments and empty lines
*.log

# This is a comment
temp/

# Another comment

test_data.txt
""")

        # Change to the temp directory to test .mudagignore auto-detection
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Initialize IgnorePatterns, which should auto-detect the .mudagignore file
            patterns = IgnorePatterns()

            # Verify patterns were loaded and empty lines/comments were skipped
            assert len(patterns.patterns) == 3
            assert patterns.patterns == ["*.log", "temp/", "test_data.txt"]
        finally:
            # Change back to the original directory
            os.chdir(original_dir)


def test_is_ignored_function() -> None:
    """Test the is_ignored function with different patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .mudagignore file with various pattern types
        with open(os.path.join(temp_dir, ".mudagignore"), "w") as mudagignore:
            mudagignore.write("""*.py
build/
output[0-9].txt
test?.xml
""")

        # Change to the temp directory to test .mudagignore auto-detection
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Initialize IgnorePatterns, which should auto-detect the .mudagignore file
            patterns = IgnorePatterns()

            # Test file extensions
            assert patterns.is_ignored("file.py") is True
            assert patterns.is_ignored("dir/module.py") is True
            assert patterns.is_ignored("file.pyc") is False

            # Test directories
            assert patterns.is_ignored("build/output.txt") is True
            assert patterns.is_ignored("path/to/build/file") is True
            assert patterns.is_ignored("builder/file.txt") is False

            # Test patterns with character classes
            assert patterns.is_ignored("output1.txt") is True
            assert patterns.is_ignored("output9.txt") is True
            assert patterns.is_ignored("output.txt") is False
            assert patterns.is_ignored("output10.txt") is False

            # Test patterns with single character wildcard
            assert patterns.is_ignored("test1.xml") is True
            assert patterns.is_ignored("testA.xml") is True
            assert patterns.is_ignored("test.xml") is False
            assert patterns.is_ignored("test12.xml") is False
        finally:
            # Change back to the original directory
            os.chdir(original_dir)
