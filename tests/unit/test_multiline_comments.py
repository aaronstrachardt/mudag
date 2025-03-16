"""Tests for multiline comment handling in the analyzer module."""

import os
import tempfile


from mudag.core.analyzer import count_lines, is_workflow_file


def test_python_docstrings() -> None:
    """Test that Python docstrings are properly counted as comments."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp_file:
        temp_file.write('''
def example_function():
    """
    This is a docstring.
    It spans multiple lines.
    All lines should be counted as comments.
    """
    # This is a regular comment
    print("Hello, world!")  # Inline comment
''')
        temp_path = temp_file.name

    try:
        result = count_lines(temp_path)
        assert result["code"] == 2  # def line and print line
        assert (
            result["comment"] == 6
        )  # 4 docstring lines, 1 regular comment, 1 inline comment
        assert result["blank"] == 1  # 1 blank line at the start
        assert result["total"] == 9  # Total lines
    finally:
        os.unlink(temp_path)


def test_python_triple_quotes() -> None:
    """Test that Python triple quoted strings are counted as comments if used as docstrings."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp_file:
        temp_file.write('''
def example_function():
    """Docstring"""
    x = """This is not a docstring but triple-quoted string"""
    y = "Regular string"
    return x
''')
        temp_path = temp_file.name

    try:
        result = count_lines(temp_path)
        assert result["code"] == 4  # def line, x = line, y = line, return line
        assert result["comment"] == 1  # Docstring only
        assert result["blank"] == 1  # 1 blank line at the start
        assert result["total"] == 6  # Total lines
    finally:
        os.unlink(temp_path)


def test_nextflow_multi_comments() -> None:
    """Test that Nextflow multiline comments are properly counted."""
    with tempfile.NamedTemporaryFile("w", suffix=".nf", delete=False) as temp_file:
        temp_file.write('''
#!/usr/bin/env nextflow

// Single line comment

/*
 * This is a multiline comment
 * in Nextflow
 */

process exampleProcess {
    input:
    val x

    output:
    val y

    script:
    """
    echo $x
    """
}
''')
        temp_path = temp_file.name

    try:
        result = count_lines(temp_path)
        # Count lines that are not comments or blank
        code_lines = (
            11  # process, input, val x, output, val y, script, """, echo $x, """, }
        )
        assert result["code"] == code_lines
        assert result["comment"] == 5  # 1 single line + 4 multiline comment lines
        assert result["blank"] == 6  # 6 blank lines
        assert result["total"] == 22
    finally:
        os.unlink(temp_path)


def test_cwl_comments() -> None:
    """Test that CWL comments are properly counted."""
    with tempfile.NamedTemporaryFile("w", suffix=".cwl", delete=False) as temp_file:
        temp_file.write("""#!/usr/bin/env cwl-runner

# This is a comment in CWL
# Another comment

cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1

outputs:
  output:
    type: stdout

stdout: output.txt
""")
        temp_path = temp_file.name

    try:
        result = count_lines(temp_path)
        assert result["comment"] == 3  # 3 comment lines (including shebang)
        assert result["blank"] == 6  # 6 blank lines
        assert result["total"] == 21
    finally:
        os.unlink(temp_path)


def test_workflow_detection() -> None:
    """Test that workflow files are correctly identified with new extensions."""
    # Test Galaxy workflow files
    assert is_workflow_file("workflow.ga") is True
    assert is_workflow_file("workflow.galaxy") is True
    assert is_workflow_file("workflow.gxwf") is True

    # Test CWL workflow files
    assert is_workflow_file("workflow.cwl") is True

    # Test Nextflow workflow files
    assert is_workflow_file("workflow.nf") is True
    assert is_workflow_file("workflow.nextflow") is True
    assert is_workflow_file("nextflow.config") is True

    # Test Snakemake workflow files
    assert is_workflow_file("Snakefile") is True
    assert is_workflow_file("workflow.smk") is True
    assert is_workflow_file("workflow.snakefile") is True
    assert is_workflow_file("workflow.snakemake") is True
    assert is_workflow_file("workflow.rules") is True

    # Test KNIME workflow files
    assert is_workflow_file("workflow.knwf") is True
    assert is_workflow_file("workflow.workflow.knime") is True

    # Test WDL workflow files
    assert is_workflow_file("workflow.wdl") is True
