import logging
from typing import List, Optional, Tuple

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel

from openai_compatible_api_probe.config import APIConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelCapabilities(BaseModel):
    """Capabilities of a specific model."""

    supports_chat: bool = False
    supports_function_calling: bool = False
    supports_structured_output: bool = False
    supports_vision: bool = False
    details: str = ""  # Will contain success details or error message


class ProbeResult(BaseModel):
    """Results of the API probe."""

    model_id: str
    capabilities: ModelCapabilities
    error_message: Optional[str] = None
    api_base: str


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

            tools: List[ChatCompletionToolParam] = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get current temperature for a given location.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City and country e.g. Bogotá, Colombia",
                                }
                            },
                            "required": ["location"],
                            "additionalProperties": False,
                        },
                    },
                }
            ]

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "What is the weather like in Paris today? Make sure you use the get_weather function.",
                    }
                ],
                tools=tools,
            )

            message = response.choices[0].message
            assert message.tool_calls is not None, message
            return True, f"Function calling successful. Response: {message}"
        except Exception as e:
            logger.warning(f"Function calling test failed for {model}: {str(e)}")
            return False, f"Function calling failed: {str(e)}"

    async def _test_structured_output(self, model: str) -> Tuple[bool, str]:
        """Test if the model supports Structured Output."""
        try:

            class CalendarEvent(BaseModel):
                name: str
                date: str
                participants: list[str]

            response = await self.client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": "Extract the event information."},
                    {
                        "role": "user",
                        "content": "Alice and Bob are going to a science fair on Friday.",
                    },
                ],
                response_format=CalendarEvent,
            )

            message = response.choices[0].message
            assert message is not None, message
            event = message.parsed
            assert event is not None, message
            assert event.name is not None, message
            assert event.date is not None, message
            assert event.participants is not None, message

            return True, f"Structured Output test successful. Response: {message}"
        except Exception as e:
            logger.warning(f"Structured Output test failed for {model}: {str(e)}")
            return False, f"Structured Output test failed: {str(e)}"

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

#           json_supported, json_details = await self._test_structured_output(model)
#           capabilities.supports_structured_output = json_supported
#           details.append(f"Structured Output: {json_details}")
#
#           vision_supported, vision_details = await self._test_vision(model)
#           capabilities.supports_vision = vision_supported
#           details.append(f"Vision: {vision_details}")

        capabilities.details = "\n".join(details)
        logger.info(f"Completed probe for model: {model}")
        return ProbeResult(
            model_id=model, capabilities=capabilities, api_base=self.config.api_base
        )

    async def list_models(self) -> List[str]:
        """List available models from the API."""
        logger.info("Fetching available models")
        models_response = await self.client.models.list()
        models = [model.id for model in models_response.data]
        logger.info(f"Found {len(models)} models")
        return models


if __name__ == "__main__":
    import asyncio

    async def main():
        probe = APIProbe()
        models = await probe.list_models()
        if models:
            logger.info(f"Testing first model: {models[0]}")
            result = await probe.probe_model(models[0])
            logger.info(f"Probe result: {result}")

    asyncio.run(main())
