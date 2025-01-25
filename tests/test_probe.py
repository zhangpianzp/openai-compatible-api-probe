from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openai_compatible_api_probe.probe import APIProbe, ModelCapabilities, ProbeResult


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock_client = MagicMock()
    mock_client.models.list = AsyncMock()
    mock_client.chat.completions.create = AsyncMock()
    return mock_client


@pytest.fixture
def probe(mock_openai_client):
    """Create a probe instance with a mock client."""
    with patch(
        "openai_compatible_api_probe.probe.AsyncOpenAI", return_value=mock_openai_client
    ):
        probe = APIProbe(api_key="test-key", api_base="https://test.api/v1")
        return probe


@pytest.mark.asyncio
async def test_list_models(probe, mock_openai_client):
    """Test that list_models returns the correct model IDs."""
    # Setup mock response
    mock_openai_client.models.list.return_value.data = [
        MagicMock(id="gpt-4"),
        MagicMock(id="gpt-3.5-turbo"),
    ]

    # Call the function
    models = await probe.list_models()

    # Verify results
    assert models == ["gpt-4", "gpt-3.5-turbo"]
    mock_openai_client.models.list.assert_called_once()


@pytest.mark.asyncio
async def test_probe_model_chat_supported(probe, mock_openai_client):
    """Test probing a model that supports chat."""
    # Setup mock responses
    mock_openai_client.chat.completions.create.side_effect = [
        # Chat completion response
        MagicMock(choices=[MagicMock(message=MagicMock(content="Hello!"))]),
        # Function calling response
        MagicMock(
            choices=[MagicMock(message=MagicMock(content="Weather function called"))]
        ),
        # JSON mode response
        MagicMock(choices=[MagicMock(message=MagicMock(content='{"status": "ok"}'))]),
        # Vision response (fails)
        Exception("Vision not supported"),
    ]

    # Call the function
    result = await probe.probe_model("gpt-4")

    # Verify results
    assert isinstance(result, ProbeResult)
    assert result.model_id == "gpt-4"
    assert result.capabilities.supports_chat is True
    assert result.capabilities.supports_function_calling is True
    assert result.capabilities.supports_json_mode is True
    assert result.capabilities.supports_vision is False
    assert "Hello!" in result.capabilities.details
    assert "Weather function called" in result.capabilities.details
    assert "Vision not supported" in result.capabilities.details


@pytest.mark.asyncio
async def test_probe_model_chat_not_supported(probe, mock_openai_client):
    """Test probing a model that doesn't support chat."""
    # Setup mock response to fail chat completion
    mock_openai_client.chat.completions.create.side_effect = Exception(
        "Chat not supported"
    )

    # Call the function
    result = await probe.probe_model("non-chat-model")

    # Verify results
    assert isinstance(result, ProbeResult)
    assert result.model_id == "non-chat-model"
    assert result.capabilities.supports_chat is False
    assert (
        result.capabilities.supports_function_calling is False
    )  # Not tested because chat failed
    assert (
        result.capabilities.supports_json_mode is False
    )  # Not tested because chat failed
    assert (
        result.capabilities.supports_vision is False
    )  # Not tested because chat failed
    assert "Chat not supported" in result.capabilities.details
