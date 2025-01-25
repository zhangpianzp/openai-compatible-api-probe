#!/bin/bash
set -e

# Run mypy type checking
echo "🔍 Running type checking with mypy..."
poetry run mypy --package openai_compatible_api_probe

# Run flake8 linting
echo "🔍 Running linting with flake8..."
poetry run flake8 openai_compatible_api_probe

# Run black formatting check
echo "🔍 Checking formatting with black..."
poetry run black --check openai_compatible_api_probe

# Run isort import sorting check
echo "🔍 Checking import sorting with isort..."
poetry run isort --check-only openai_compatible_api_probe

echo "✅ All checks passed!" 