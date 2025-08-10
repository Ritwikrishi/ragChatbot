#!/bin/bash
# Code formatting script

set -e

echo "Running code quality checks and formatting..."

echo "1. Running isort..."
uv run isort backend/ main.py

echo "2. Running black..."
uv run black backend/ main.py

echo "3. Running flake8..."
uv run flake8 backend/ main.py

echo "All formatting and checks completed!"