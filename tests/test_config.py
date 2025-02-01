import os
from unittest.mock import patch

import pytest

from openai_compatible_api_probe.config import APIConfig


def test_config_from_env_vars():
    """Test that config properly reads from environment variables."""
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key", "OPENAI_API_BASE": "https://test.api/v1"},
        clear=True,
    ):  # Clear existing env vars
        config = APIConfig()
        assert config.api_key == "test-key"
        assert config.api_base == "https://test.api/v1"


def test_config_validation():
    """Test that config validation works correctly."""
    with patch.dict(os.environ, {}, clear=True):
        # Test with missing API key
        config = APIConfig(api_base="https://test.api/v1")
        assert config.validate_config() is False

        # Test with valid config
        config = APIConfig(api_key="test-key", api_base="https://test.api/v1")
        assert config.validate_config() is True
