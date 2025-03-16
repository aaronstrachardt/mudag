#!/usr/bin/env python3
"""
Example script demonstrating how to use Mudag as a Python API.
"""

import os
import tempfile
from mudag.core.analyzer import count_lines, is_workflow_file, scan_directory


def main():
    """Main entry point for the example script."""
    print("Mudag API Example")
    print("================")

    # Example 1: Check if a file is a workflow file
    example_files = [
        "workflow.cwl",
        "Snakefile",
        "pipeline.nf",
        "analysis.ga",
        "script.py",
    ]

    print("\nExample 1: Checking workflow file types")
    print("-------------------------------------")
    for file in example_files:
        result = is_workflow_file(file)
        print(f"Is '{file}' a workflow file? {result}")

    # Example 2: Count lines in a file
    if os.path.exists("examples/workflow.cwl"):
        print("\nExample 2: Counting lines in a CWL file")
        print("------------------------------------")
        lines = count_lines("examples/workflow.cwl")
        print("File: examples/workflow.cwl")
        print(f"  Code lines:    {lines['code']}")
        print(f"  Comment lines: {lines['comment']}")
        print(f"  Blank lines:   {lines['blank']}")
        print(f"  Total lines:   {lines['total']}")

    # Example 3: Scan a directory for workflow files
    print("\nExample 3: Scanning a directory")
    print("---------------------------")

    # Create a temporary directory with a .mudagignore file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a .mudagignore file in the temporary directory
        with open(os.path.join(temp_dir, ".mudagignore"), "w") as mudagignore:
            mudagignore.write("""# Temporary mudagignore file for example
*.log
node_modules/
__pycache__/
""")

        # Create a test workflow file
        with open(os.path.join(temp_dir, "test.cwl"), "w") as cwl_file:
            cwl_file.write("""# Test CWL file
cwlVersion: v1.0
class: CommandLineTool
""")

        # Create an ignored file
        with open(os.path.join(temp_dir, "test.log"), "w") as log_file:
            log_file.write("This file should be ignored")

        # Create a subdirectory with a workflow file
        os.makedirs(os.path.join(temp_dir, "subdir"))
        with open(os.path.join(temp_dir, "subdir", "workflow.cwl"), "w") as cwl_file2:
            cwl_file2.write("""# Another CWL file
cwlVersion: v1.0
class: Workflow
""")

        # Change to the temp directory so the .mudagignore file is found
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Scan the current directory
            print(f"Scanning directory: {temp_dir}")
            results = scan_directory(".")

            # Pretty print the results
            num_files = len(results) - 1 if "__metadata__" in results else len(results)
            print(f"Found {num_files} workflow files:")

            for file_path, counts in results.items():
                if file_path == "__metadata__":
                    continue

                print(f"\n{file_path}:")
                print(f"  Code lines:    {counts['code']}")
                print(f"  Comment lines: {counts['comment']}")
                print(f"  Blank lines:   {counts['blank']}")
                print(f"  Total lines:   {counts['total']}")

            # Example 4: Print workflow language statistics
            if (
                "__metadata__" in results
                and "workflow_languages" in results["__metadata__"]
            ):
                print("\nExample 4: Workflow language statistics")
                print("-----------------------------------")

                lang_stats = results["__metadata__"]["workflow_languages"]
                for lang, stats in lang_stats.items():
                    if stats["files"] > 0:
                        print(
                            f"{lang}: {stats['files']} files, {stats['total']} total lines"
                        )
        finally:
            # Change back to the original directory
            os.chdir(original_dir)


if __name__ == "__main__":
    main()
