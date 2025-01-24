# OpenAI Compatible API Probe

A Python tool to probe and analyze OpenAI-compatible APIs, checking for model availability and feature support across different providers.

## Features

- Discovers available models from any OpenAI-compatible API endpoint
- Tests model capabilities for:
  - Function calling
  - Structured input/output
  - Image handling (multi-modality)
  - Chat completions
  - Embeddings
- Generates machine-readable reports of API capabilities
- CLI tool for easy probing and reporting
- Flexible configuration via environment variables or direct parameters

## Installation

```bash
pip install openai-compatible-api-probe
```

Or install from source:

```bash
git clone https://github.com/yourusername/openai-compatible-api-probe.git
cd openai-compatible-api-probe
poetry install
```

## Usage

### Command Line Interface

```bash
# Using environment variables
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.provider.com/v1"
openai-probe

# Or specify directly
openai-probe --api-key "your-api-key" --api-base "https://api.provider.com/v1"
```

### Python API

```python
from openai_compatible_api_probe import APIProbe

# Using environment variables
probe = APIProbe()

# Or specify directly
probe = APIProbe(
    api_key="your-api-key",
    api_base="https://api.provider.com/v1"
)

# Run the probe and get results
results = probe.run()
print(results.to_dict())  # Get machine-readable results
print(results.to_markdown())  # Get human-readable report
```

## Environment Variables

- `OPENAI_API_KEY`: Your API key
- `OPENAI_API_BASE`: Base URL of the API endpoint
- `OPENAI_API_VERSION`: (Optional) API version if required
- `OPENAI_ORGANIZATION`: (Optional) Organization ID if required

## Development

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run flake8
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 