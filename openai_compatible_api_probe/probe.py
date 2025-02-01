import logging
from typing import List, Optional, Tuple

from openai import AsyncOpenAI
from pydantic import BaseModel

from .config import APIConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelCapabilities(BaseModel):
    """Capabilities of a specific model."""

    supports_chat: bool = False
    supports_function_calling: bool = False
    supports_json_mode: bool = False
    supports_vision: bool = False
    details: str = ""  # Will contain success details or error message


class ProbeResult(BaseModel):
    """Results of the API probe."""

    model_id: str
    capabilities: ModelCapabilities
    error_message: Optional[str] = None


class APIProbe:
    def __init__(
        self, api_key: Optional[str] = None, api_base: Optional[str] = None
    ) -> None:
        """Initialize the API probe with optional configuration."""
        # Handle Typer options by getting their default values
        if hasattr(api_key, "default"):
            api_key = None
        if hasattr(api_base, "default"):
            api_base = None

        self.config = APIConfig()
        if api_key:
            self.config.api_key = api_key
        if api_base:
            self.config.api_base = api_base

        logger.info(f"Initializing probe with base URL: {self.config.api_base}")
        self.client: AsyncOpenAI
        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the OpenAI client with the provided configuration."""
        if not self.config.validate_config():
            raise ValueError("API key and base URL are required")

        try:
            self.client = AsyncOpenAI(
                api_key=self.config.api_key, base_url=self.config.api_base
            )
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    async def _test_chat_completion(self, model: str) -> Tuple[bool, str]:
        """Test if the model supports chat completion."""
        try:
            logger.info(f"Testing chat completion for model: {model}")
            response = await self.client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": "Hello"}]
            )
            message = response.choices[0].message
            assert message.content is not None
            return True, f"Chat completion successful. Response: {message}"
        except Exception as e:
            logger.warning(f"Chat completion test failed for {model}: {str(e)}")
            return False, f"Chat completion failed: {str(e)}"

    async def _test_function_calling(self, model: str) -> Tuple[bool, str]:
        """Test if the model supports function calling."""
        try:
            logger.info(f"Testing function calling for model: {model}")
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "What's the weather like in Tokyo?"}
                ],
                functions=[
                    {
                        "name": "get_weather",
                        "description": "Get the weather in a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string"},
                                "unit": {
                                    "type": "string",
                                    "enum": ["celsius", "fahrenheit"],
                                },
                            },
                        },
                    }
                ],
            )
            message = response.choices[0].message
            assert message.function_call is not None
            return True, f"Function calling successful. Response: {message}"
        except Exception as e:
            logger.warning(f"Function calling test failed for {model}: {str(e)}")
            return False, f"Function calling failed: {str(e)}"

    async def _test_json_mode(self, model: str) -> Tuple[bool, str]:
        """Test if the model supports JSON mode."""
        try:
            logger.info(f"Testing JSON mode for model: {model}")
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Return a simple JSON object"}],
                response_format={"type": "json_object"},
            )
            message = response.choices[0].message
            return True, f"JSON mode successful. Response: {message}"
        except Exception as e:
            logger.warning(f"JSON mode test failed for {model}: {str(e)}")
            return False, f"JSON mode failed: {str(e)}"

    async def _test_vision(self, model: str) -> Tuple[bool, str]:
        """Test if the model supports vision features."""
        try:
            logger.info(f"Testing vision features for model: {model}")
            # Use a minimal 1x1 transparent PNG for testing
            test_image = (
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0"
                "lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            )
            await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What's in this image?"},
                            {"type": "image_url", "image_url": {"url": test_image}},
                        ],
                    }
                ],
            )
            return True, "Vision features supported"
        except Exception as e:
            logger.warning(f"Vision test failed for {model}: {str(e)}")
            return False, f"Vision features not supported: {str(e)}"

    async def probe_model(self, model: str) -> ProbeResult:
        """Probe a specific model for its capabilities."""
        logger.info(f"Starting probe for model: {model}")
        capabilities = ModelCapabilities()
        details = []

        # Test chat completion first
        chat_supported, chat_details = await self._test_chat_completion(model)
        capabilities.supports_chat = chat_supported
        details.append(f"Chat: {chat_details}")

        # Only test these if chat is supported
        if chat_supported:
            func_supported, func_details = await self._test_function_calling(model)
            capabilities.supports_function_calling = func_supported
            details.append(f"Functions: {func_details}")

            json_supported, json_details = await self._test_json_mode(model)
            capabilities.supports_json_mode = json_supported
            details.append(f"JSON Mode: {json_details}")

            vision_supported, vision_details = await self._test_vision(model)
            capabilities.supports_vision = vision_supported
            details.append(f"Vision: {vision_details}")

        capabilities.details = "\n".join(details)
        logger.info(f"Completed probe for model: {model}")
        return ProbeResult(model_id=model, capabilities=capabilities)

    async def list_models(self) -> List[str]:
        """List available models from the API."""
        logger.info("Fetching available models")
        models_response = await self.client.models.list()
        models = [model.id for model in models_response.data]
        logger.info(f"Found {len(models)} models")
        return models
