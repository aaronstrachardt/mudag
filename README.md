# Mudag

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A CLI tool for analyzing research software repositories with a focus on workflow languages. Mudag helps researchers and developers count code, comments, and blank lines in various workflow language files to understand code complexity and documentation levels.

## Features

- Count code lines, comment lines, and blank lines in files
- Focus on workflow languages used in scientific research:
  - Common Workflow Language (CWL)
  - Snakemake
  - Nextflow
  - Galaxy
  - KNIME
- Support for scanning individual files or entire directories
- Multiple output formats (table, JSON, CSV)
- Automatic file and directory exclusion using `.mudagignore` patterns (similar to `.gitignore`)

## Installation

### From GitHub

```bash
# Clone the repository
git clone https://github.com/aaronstrachardt/mudag.git
cd mudag

# Create and activate Virtual Environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

### Requirements

- Python 3.7+
- No external dependencies required

## Usage

### Analyze a File or Directory

```bash
# Analyze workflow files in a directory
mudag analyze path/to/directory

# Analyze a specific file
mudag analyze path/to/file.cwl

# Choose output format
mudag analyze path/to/directory --format json

# Save output to a file
mudag analyze path/to/directory --output results.json
```

### List Workflow Files

```bash
# List all workflow files in a directory
mudag list-workflows path/to/directory
```

## Supported Workflow Languages

| Language | Extensions |
|----------|------------|
| Common Workflow Language | `.cwl` |
| Snakemake | `Snakefile`, `.smk`, `.snake`, `.snakefile`, `.snakemake`, `.rules`, `.rule` |
| Nextflow | `.nf`, `.nextflow`, `.config` |
| Galaxy | `.ga`, `.galaxy`, `.gxwf` |
| KNIME | `.knwf`, `.workflow.knime`, `.knar` |

## Output Formats

### Table (default)

```
File Path         | Code    | Comment | Blank   | Total   
------------------------------------------------
path/to/file1.cwl | 10      | 5       | 2       | 17      
path/to/file2.smk | 20      | 10      | 5       | 35      
------------------------------------------------
TOTAL             | 30      | 15      | 7       | 52      
```

### JSON

```json
{
  "summary": {
    "total_files": 2,
    "total_code": 30,
    "total_comment": 15,
    "total_blank": 7,
    "total_lines": 52
  },
  "files": {
    "path/to/file1.cwl": {
      "code": 10,
      "comment": 5,
      "blank": 2,
      "total": 17
    },
    "path/to/file2.smk": {
      "code": 20,
      "comment": 10,
      "blank": 5,
      "total": 35
    }
  }
}
```

### CSV

```csv
File Path,Code Lines,Comment Lines,Blank Lines,Total Lines
path/to/file1.cwl,10,5,2,17
path/to/file2.smk,20,10,5,35
TOTAL,30,15,7,52
```

## Configuration Options

### Using .mudagignore Files

Mudag automatically uses `.mudagignore` files to exclude files and directories from analysis. This allows you to specify patterns of files and directories to exclude, similar to how `.gitignore` works.

#### Creating a .mudagignore File

You can create a `.mudagignore` file in the following locations:

1. **Project-specific**: In the root directory of your project
2. **Global**: In your home directory (`~/.mudagignore`)

Example `.mudagignore` file:

```
# Default directories to ignore
.git/
__pycache__/
node_modules/
venv/
env/

# Ignore all .log files
*.log

# Ignore specific directories
temp/
old_workflows/

# Ignore specific files
broken_workflow.cwl
test_data.fa
```

The ignore patterns support glob patterns similar to `.gitignore`:

- `*` matches any number of characters
- `?` matches a single character
- `[abc]` matches any character in the set
- Lines starting with `#` are treated as comments

## Development

### Testing

To run the tests for Mudag:

```bash
# Run all tests
python3 -m pytest tests -v

# Run specific tests
python3 -m pytest tests/unit/test_analyzer.py -v
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
