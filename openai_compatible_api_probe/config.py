import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class APIConfig(BaseModel):
    """Configuration for OpenAI-compatible API endpoints."""

    api_key: str = Field(
        default=os.getenv("OPENAI_API_KEY", ""),
        description="API key for authentication",
    )
    api_base: str = Field(
        default=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        description="Base URL for the API endpoint",
    )

    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        return bool(self.api_key and self.api_base)
