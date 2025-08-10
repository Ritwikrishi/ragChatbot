#!/bin/bash
# Complete code quality check script

set -e

echo "Running complete code quality checks..."

echo "1. Checking import order with isort..."
uv run isort --check-only --diff backend/ main.py

echo "2. Checking code formatting with black..."
uv run black --check --diff backend/ main.py

echo "3. Running flake8 linting..."
uv run flake8 backend/ main.py

echo "4. Running mypy type checking..."
uv run mypy backend/ main.py

echo "All quality checks passed!"