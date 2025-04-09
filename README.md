# OpenAI Compatible API Probe

A Python tool to probe and analyze OpenAI-compatible APIs, checking for model availability and feature support across different providers. This is useful when working with alternative AI providers that offer OpenAI-compatible endpoints (like Groq, Fireworks, Anyscale, etc.) to understand which features are supported.

## 安装pip包

pip install openai-compatible-test-0.1.0-py3-none-any.whl

## 设置环境变量

OPENAI_API_KEY=**

OPENAI_API_BASE=https://openai.test/v1


## 执行命令

openai-probe

## 按指引进行测试

1. 列出模型
2. 输入模型名字，进行兼容性测试


## Features

The probe tests each model for support of:
- Chat completions (basic chat functionality)
- Function calling (ability to define and call functions)
- Structured output (structured JSON output)
- Vision capabilities (ability to process images)

For each feature, it provides detailed information about:
- Whether the feature is supported
- The actual API response or error message received
- Any specific limitations or requirements

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

### Basic Usage

Simply run the command to start in interactive mode:

```bash
openai-probe
```

This will automatically:
1. Load API settings from your `.env` file
2. Start the interactive interface where you can:
   - List all available models
   - Probe a specific model
   - Probe models matching a pattern
   - Probe all available models

### Command Line Options

```bash
# Show help and available options
openai-probe --help

# Override API key from .env
openai-probe --api-key "your-api-key"

# Use a different API endpoint
openai-probe --api-base "https://api.groq.com/v1"

# Get JSON output instead of tables
openai-probe --json
```

### Environment Variables

The tool automatically reads from your `.env` file. Create one with:

```
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.provider.com/v1
```

### Python API

You can also use the tool programmatically in your Python code:

```python
from openai_compatible_api_probe import APIProbe

# Initialize the probe
probe = APIProbe(
    api_key="your-api-key",
    api_base="https://api.provider.com/v1"
)

# List available models
models = await probe.list_models()

# Probe a specific model
result = await probe.probe_model("gpt-4")

# Check capabilities
if result.capabilities.supports_chat:
    print("Model supports chat!")
if result.capabilities.supports_function_calling:
    print("Model supports function calling!")

# Get detailed results
print(result.model_dump_json(indent=2))
```

## Example Output

When probing a model, you'll see a table like this:

```
                       OpenAI API Compatibility Report - gpt-4                       
                          API URL: https://api.openai.com/v1
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Feature           ┃ Supported ┃ Details                                         ┃
┣━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Chat             ┃ ✓         ┃ Chat completion successful                      ┃
┣━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Functions        ┃ ✓         ┃ Function calling successful                     ┃
┣━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

```

## Common Use Cases

1. **API Provider Evaluation**: When choosing between different OpenAI-compatible providers, quickly compare their feature support.
2. **Compatibility Testing**: Before deploying your application with a new provider, verify that all required features are supported.
3. **Model Selection**: Find models that support specific features like function calling or structured output.
4. **API Integration**: Debug API integration issues by understanding exactly which features work and which don't.

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