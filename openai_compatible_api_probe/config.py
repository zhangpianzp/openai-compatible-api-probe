import os

from dotenv import load_dotenv
from pydantic import BaseModel


def load_env_vars() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


class APIConfig(BaseModel):
    """Configuration for OpenAI-compatible API endpoints."""

    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"

    def __init__(self, **data: dict[str, str]) -> None:
        """Initialize config with optional data or environment variables."""
        super().__init__(**data)
        if not data:  # Only load from env if no data provided
            self.refresh_from_env()

    def refresh_from_env(self) -> None:
        """Refresh config values from environment variables."""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.api_base = os.getenv("OPENAI_API_BASE", "")

    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        return bool(self.api_key and self.api_base)
