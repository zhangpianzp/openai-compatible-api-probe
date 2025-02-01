#!/bin/bash
set -e

# Run tests with coverage
echo "🧪 Running tests with pytest and coverage..."
poetry run pytest tests/ --cov=openai_compatible_api_probe --cov-report=html --cov-report=term-missing --cov-fail-under=80

echo "✅ All checks passed!" 