#!/bin/bash
set -e

echo "🎨 Running code formatters..."

echo "Running black..."
poetry run black openai_compatible_api_probe/ tests/

echo "Running isort..."
poetry run isort openai_compatible_api_probe/ tests/

echo "Running autopep8..."
poetry run autopep8 --in-place --recursive --max-line-length 88 openai_compatible_api_probe/ tests/

echo "✨ All formatting complete!" 