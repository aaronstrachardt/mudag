"""Unit tests for the formatter module."""

import io
from typing import Dict, List, TextIO

import pytest

from mudag.utils.formatter import format_csv, format_json, format_table


@pytest.fixture
def sample_results() -> Dict[str, Dict[str, int]]:
    """
    Create a fixture with sample results.
    
    Returns:
        Dictionary with sample results
    """
    return {
        "/path/to/file1.cwl": {
            "code": 10,
            "comment": 5,
            "blank": 2,
            "total": 17
        },
        "/path/to/file2.smk": {
            "code": 20,
            "comment": 10,
            "blank": 5,
            "total": 35
        }
    }


def test_format_table(sample_results: Dict[str, Dict[str, int]]) -> None:
    """
    Test the table formatter.
    
    Args:
        sample_results: Fixture with sample results
    """
    output = io.StringIO()
    format_table(sample_results, output)
    
    # Reset string IO cursor
    output.seek(0)
    
    # Check output
    lines = output.readlines()
    
    # The first line should be the total files analyzed
    assert "Total files analyzed: 2" in lines[0]
    
    # There should be a blank line next
    assert lines[1].strip() == ""
    
    # Now check the header (line 2)
    assert "No." in lines[2]
    assert "File Path" in lines[2]
    assert "Code" in lines[2]
    assert "Comment" in lines[2]
    assert "Blank" in lines[2]
    assert "Total" in lines[2]
    
    # Check separator (line 3)
    assert "-" in lines[3]
    
    # Check data (lines 4 and 5)
    assert "file1.cwl" in lines[4]
    assert "10" in lines[4]
    assert "5" in lines[4]
    assert "2" in lines[4]
    assert "17" in lines[4]
    
    assert "file2.smk" in lines[5]
    assert "20" in lines[5]
    assert "10" in lines[5]
    assert "5" in lines[5]
    assert "35" in lines[5]
    
    # Check separator (line 6)
    assert "-" in lines[6]
    
    # Check totals (line 7)
    assert "TOTAL" in lines[7]
    assert "30" in lines[7]
    assert "15" in lines[7]
    assert "7" in lines[7]
    assert "52" in lines[7]


def test_format_json(sample_results: Dict[str, Dict[str, int]]) -> None:
    """
    Test the JSON formatter.
    
    Args:
        sample_results: Fixture with sample results
    """
    output = io.StringIO()
    format_json(sample_results, output)
    
    # Reset string IO cursor
    output.seek(0)
    
    # Check output
    json_str = output.read()
    
    # Check that it contains key elements
    assert "summary" in json_str
    assert "total_files" in json_str
    assert "total_code" in json_str
    assert "total_comment" in json_str
    assert "total_blank" in json_str
    assert "total_lines" in json_str
    assert "files" in json_str
    assert "/path/to/file1.cwl" in json_str
    assert "/path/to/file2.smk" in json_str
    
    # Check values
    assert "30" in json_str  # total code
    assert "15" in json_str  # total comment
    assert "7" in json_str   # total blank
    assert "52" in json_str  # total lines
    assert "2" in json_str   # total files


def test_format_csv(sample_results: Dict[str, Dict[str, int]]) -> None:
    """
    Test the CSV formatter.
    
    Args:
        sample_results: Fixture with sample results
    """
    output = io.StringIO()
    format_csv(sample_results, output)
    
    # Reset string IO cursor
    output.seek(0)
    
    # Check output
    lines = output.readlines()
    
    # Check header
    assert "File Path" in lines[0]
    assert "Code Lines" in lines[0]
    assert "Comment Lines" in lines[0]
    assert "Blank Lines" in lines[0]
    assert "Total Lines" in lines[0]
    
    # Check data
    assert "/path/to/file1.cwl" in lines[1]
    assert "10" in lines[1]
    assert "5" in lines[1]
    assert "2" in lines[1]
    assert "17" in lines[1]
    
    assert "/path/to/file2.smk" in lines[2]
    assert "20" in lines[2]
    assert "10" in lines[2]
    assert "5" in lines[2]
    assert "35" in lines[2]
    
    # Check totals
    assert "TOTAL" in lines[3]
    assert "30" in lines[3]
    assert "15" in lines[3]
    assert "7" in lines[3]
    assert "52" in lines[3] 