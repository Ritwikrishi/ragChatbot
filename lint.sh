#!/bin/bash
# Linting script

set -e

echo "Running linting checks..."

echo "1. Running flake8..."
uv run flake8 backend/ main.py

echo "2. Running mypy..."
uv run mypy backend/ main.py

echo "All linting checks completed!"