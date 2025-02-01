"""Tests for the CLI module."""

import os

import pytest
from typer.testing import CliRunner

from openai_compatible_api_probe.cli import app
from openai_compatible_api_probe.probe import ModelCapabilities, ProbeResult


def test_version():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "OpenAI API Probe" in result.stdout


@pytest.mark.asyncio
async def test_probe_models(monkeypatch):
    """Test probe_models command."""
    # Mock environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE", "https://test.api/v1")

    # Mock probe results
    mock_models = ["gpt-4", "gpt-3.5-turbo"]
    mock_results = {
        "gpt-4": ModelCapabilities(
            supports_chat=True,
            supports_function_calling=True,
            supports_json_mode=True,
            supports_vision=False,
        ),
        "gpt-3.5-turbo": ModelCapabilities(
            supports_chat=True,
            supports_function_calling=True,
            supports_json_mode=True,
            supports_vision=False,
        ),
    }

    # Mock list_models function
    async def mock_list_models(self):
        return mock_models

    # Mock probe_model function
    async def mock_probe_model(self, model):
        return ProbeResult(model_id=model, capabilities=mock_results[model])

    # Apply the mocks
    from openai_compatible_api_probe.probe import APIProbe

    monkeypatch.setattr(APIProbe, "list_models", mock_list_models)
    monkeypatch.setattr(APIProbe, "probe_model", mock_probe_model)

    # Run the command
    runner = CliRunner()
    result = runner.invoke(app, ["probe-models"])
    assert result.exit_code == 0
    assert "gpt-4" in result.stdout
    assert "gpt-3.5-turbo" in result.stdout


@pytest.mark.asyncio
async def test_probe_pattern(monkeypatch):
    """Test probe_pattern command."""
    # Mock environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE", "https://test.api/v1")

    # Mock probe results
    mock_models = ["gpt-4"]
    mock_results = {
        "gpt-4": ModelCapabilities(
            supports_chat=True,
            supports_function_calling=True,
            supports_json_mode=True,
            supports_vision=False,
        ),
    }

    # Mock list_models function
    async def mock_list_models(self):
        return mock_models

    # Mock probe_model function
    async def mock_probe_model(self, model):
        return ProbeResult(model_id=model, capabilities=mock_results[model])

    # Apply the mocks
    from openai_compatible_api_probe.probe import APIProbe

    monkeypatch.setattr(APIProbe, "list_models", mock_list_models)
    monkeypatch.setattr(APIProbe, "probe_model", mock_probe_model)

    # Run the command
    runner = CliRunner()
    result = runner.invoke(app, ["probe-pattern", "gpt-4"])
    assert result.exit_code == 0
    assert "gpt-4" in result.stdout


@pytest.mark.asyncio
async def test_interactive_menu(monkeypatch):
    """Test interactive menu."""
    # Mock environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE", "https://test.api/v1")

    # Mock probe results
    mock_models = ["gpt-4"]
    mock_results = {
        "gpt-4": ModelCapabilities(
            supports_chat=True,
            supports_function_calling=True,
            supports_json_mode=True,
            supports_vision=False,
        ),
    }

    # Mock list_models function
    async def mock_list_models(self):
        return mock_models

    # Mock probe_model function
    async def mock_probe_model(self, model):
        return ProbeResult(model_id=model, capabilities=mock_results[model])

    # Apply the mocks
    from openai_compatible_api_probe.probe import APIProbe

    monkeypatch.setattr(APIProbe, "list_models", mock_list_models)
    monkeypatch.setattr(APIProbe, "probe_model", mock_probe_model)

    # Run the command
    runner = CliRunner()
    result = runner.invoke(app, ["interactive"], input="1\n1\n3\n")
    assert result.exit_code == 0
    assert "Main Menu" in result.stdout
