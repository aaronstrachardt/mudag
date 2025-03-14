# Contributing to Mudag

Thank you for considering contributing to Mudag! Here are some guidelines to help you get started.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/aaronstrachardt/mudag.git
   ```
3. Install in development mode:
   ```bash
   cd mudag
   pip install -e .
   ```

## Running Tests

Tests are written using pytest:

```bash
# Run all tests
PYTHONPATH=src python3 -m pytest tests -v

# Run specific tests
PYTHONPATH=src python3 -m pytest tests/unit/test_analyzer.py -v
```

## Code Style

Please follow these coding standards:

- Use [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write docstrings for all functions, classes, and modules
- Include type hints where appropriate
- Keep line length to 88 characters or less

## Submitting Changes

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit them:
   ```bash
   git commit -m "Description of your changes"
   ```
3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
4. Submit a pull request from your fork to the main repository

## Feature Requests and Bug Reports

Please use the GitHub issue tracker to submit feature requests and bug reports.

## Adding Support for New Workflow Languages

To add support for a new workflow language:

1. Update the `is_workflow_file` function in `src/mudag/core/analyzer.py`
2. Add appropriate comment detection in `count_lines` for the language
3. Add tests for the new language
4. Update the documentation in README.md

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. 