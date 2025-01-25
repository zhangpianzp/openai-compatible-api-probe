import os
from unittest.mock import patch

import pytest

from openai_compatible_api_probe.config import APIConfig


def test_config_from_env_vars():
    """Test that config properly reads from environment variables."""
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key", "OPENAI_API_BASE": "https://test.api/v1"},
    ):
        config = APIConfig()
        assert config.api_key == "test-key"
        assert config.api_base == "https://test.api/v1"
        assert config.validate_config() is True


def test_config_validation():
    """Test that config validation works correctly."""
    # Test with missing API key
    config = APIConfig(api_base="https://test.api/v1")
    assert config.validate_config() is False

    # Test with missing base URL
    config = APIConfig(api_key="test-key")
    assert config.validate_config() is False

    # Test with both values
    config = APIConfig(api_key="test-key", api_base="https://test.api/v1")
    assert config.validate_config() is True


def test_config_defaults():
    """Test that config uses correct defaults."""
    config = APIConfig()
    assert config.api_key == ""  # Default when env var not set
    assert config.api_base == "https://api.openai.com/v1"  # Default OpenAI API URL
